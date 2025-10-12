// fastscreenocr.mm  (macOS 15+ / ScreenCaptureKit, no Swift)
// Adds: --server (stdin-triggered captures) and --loop N [--sleep-ms M].
// Prints ONE compact JSON line per capture and flushes.
// Build:
//   clang++ -std=c++17 -fobjc-arc \
//     -framework Foundation -framework CoreGraphics -framework Vision -framework ScreenCaptureKit \
//     fastscreenocr.mm -o fastscreenocr

#import <Foundation/Foundation.h>
#import <CoreGraphics/CoreGraphics.h>
#import <Vision/Vision.h>
#import <ScreenCaptureKit/ScreenCaptureKit.h>

static inline void normalizedToPixelTopLeftBottomRight(CGRect norm,
                                                       size_t imgW, size_t imgH,
                                                       double outTL[2], double outBR[2]) {
    double x1 = norm.origin.x * (double)imgW;
    double y1 = (1.0 - (norm.origin.y + norm.size.height)) * (double)imgH; // top-left y
    double x2 = (norm.origin.x + norm.size.width) * (double)imgW;
    double y2 = (1.0 - norm.origin.y) * (double)imgH;                      // bottom-right y
    outTL[0] = x1; outTL[1] = y1; outBR[0] = x2; outBR[1] = y2;
}

static NSArray<NSString *>* envLanguageHints() {
    const char *env = getenv("FASTSCREENOCR_LANGS");
    if (!env) return nil;
    NSString *str = [NSString stringWithUTF8String:env];
    NSMutableArray *langs = [NSMutableArray array];
    for (NSString *tok in [str componentsSeparatedByString:@","]) {
        NSString *t = [tok stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
        if (t.length) [langs addObject:t];
    }
    return langs.count ? langs : nil;
}

// ---- Cached ScreenCaptureKit objects (reused in server/loop modes) ----
static SCContentFilter *g_filter = nil;
static SCStreamConfiguration *g_cfg = nil;

static BOOL EnsureFilterAndConfig(void) {
    if (g_filter && g_cfg) return YES;

    __block BOOL ok = NO;
    dispatch_semaphore_t sem = dispatch_semaphore_create(0);

    [SCShareableContent getShareableContentWithCompletionHandler:^(SCShareableContent * _Nullable content,
                                                                   NSError * _Nullable err1)
    {
        if (!content || err1 || content.displays.count == 0) {
            dispatch_semaphore_signal(sem);
            return;
        }
        CGDirectDisplayID mainID = CGMainDisplayID();
        SCDisplay *mainDisplay = nil;
        for (SCDisplay *d in content.displays) {
            if (d.displayID == mainID) { mainDisplay = d; break; }
        }
        if (!mainDisplay) mainDisplay = content.displays.firstObject;
        if (!mainDisplay) { dispatch_semaphore_signal(sem); return; }

        g_filter = [[SCContentFilter alloc] initWithDisplay:mainDisplay excludingWindows:@[]];

        g_cfg = [SCStreamConfiguration new];
        g_cfg.capturesAudio = NO;
        g_cfg.showsCursor = NO;
        g_cfg.preservesAspectRatio = YES;

        CGRect  pts   = g_filter.contentRect;     // points
        CGFloat scale = g_filter.pointPixelScale; // points -> pixels
        g_cfg.width  = (NSInteger)llround(pts.size.width  * scale);
        g_cfg.height = (NSInteger)llround(pts.size.height * scale);

        ok = YES;
        dispatch_semaphore_signal(sem);
    }];

    dispatch_time_t timeout = dispatch_time(DISPATCH_TIME_NOW, (int64_t)(3.0 * NSEC_PER_SEC));
    (void)dispatch_semaphore_wait(sem, timeout);
    return ok;
}

// One-shot capture using cached filter/config.
// Returns retained CGImageRef or NULL on failure.
static CGImageRef CaptureOnceCGImage(void) {
    if (!EnsureFilterAndConfig()) return NULL;

    __block CGImageRef result = NULL;
    dispatch_semaphore_t sem = dispatch_semaphore_create(0);

    [SCScreenshotManager captureImageWithFilter:g_filter
                                   configuration:g_cfg
                               completionHandler:^(CGImageRef _Nullable image, NSError * _Nullable err2)
    {
        if (image && !err2) result = CGImageRetain(image);
        dispatch_semaphore_signal(sem);
    }];

    dispatch_time_t timeout = dispatch_time(DISPATCH_TIME_NOW, (int64_t)(3.0 * NSEC_PER_SEC));
    (void)dispatch_semaphore_wait(sem, timeout);
    return result; // NULL if failed
}

// Perform capture+OCR and (optionally) emit compact JSON array to stdout.
// Returns YES if OCR ran (even if 0 words), NO on fatal capture/OCR error.
static BOOL CaptureAndMaybeEmitJSON(NSArray *langs, BOOL emitJSON) {
    CGImageRef cgimg = CaptureOnceCGImage();
    if (!cgimg) {
        if (emitJSON) { fwrite("[]\n", 1, 3, stdout); fflush(stdout); }
        return NO;
    }
    const size_t imgW = CGImageGetWidth(cgimg);
    const size_t imgH = CGImageGetHeight(cgimg);

    VNRecognizeTextRequest *req = [[VNRecognizeTextRequest alloc] init];
    req.recognitionLevel = VNRequestTextRecognitionLevelFast;
    req.usesLanguageCorrection = NO;
    if (langs) req.recognitionLanguages = langs;

    NSError *perr = nil;
    VNImageRequestHandler *handler = [[VNImageRequestHandler alloc] initWithCGImage:cgimg options:@{}];
    BOOL ok = [handler performRequests:@[req] error:&perr];
    CGImageRelease(cgimg);

    if (!ok || perr) {
        if (emitJSON) { fwrite("[]\n", 1, 3, stdout); fflush(stdout); }
        return NO;
    }

    if (!emitJSON) return YES;

    // Build output (compact JSON)
    NSMutableArray *outItems = [NSMutableArray arrayWithCapacity:256];
    NSArray<VNRecognizedTextObservation*> *results = (NSArray<VNRecognizedTextObservation*>*)req.results;
    for (VNRecognizedTextObservation *obs in results) {
        VNRecognizedText *best = [obs topCandidates:1].firstObject;
        if (!best || !best.string.length) continue;

        NSString *line = best.string;
        [line enumerateSubstringsInRange:NSMakeRange(0, line.length)
                                 options:NSStringEnumerationByWords
                              usingBlock:^(NSString * _Nullable word,
                                           NSRange wordRange,
                                           NSRange enclosingRange,
                                           BOOL * _Nonnull stop)
        {
            if (!word || !word.length) return;
            NSError *bboxErr = nil;
            VNRectangleObservation *rectObs = [best boundingBoxForRange:wordRange error:&bboxErr];
            if (!rectObs || bboxErr) return;

            CGRect b = rectObs.boundingBox;
            double tl[2], br[2];
            normalizedToPixelTopLeftBottomRight(b, imgW, imgH, tl, br);
            [outItems addObject:@{ @"word": word,
                                   @"top_left": @[@(tl[0]), @(tl[1])],
                                   @"bottom_right": @[@(br[0]), @(br[1])] }];
        }];
    }

    NSError *jerr = nil;
    NSData *json = [NSJSONSerialization dataWithJSONObject:outItems options:0 error:&jerr];
    if (!json || jerr) {
        fwrite("[]\n", 1, 3, stdout); fflush(stdout);
        return NO;
    }
    fwrite(json.bytes, 1, json.length, stdout);
    fputc('\n', stdout);
    fflush(stdout);
    return YES;
}

static void server_loop(NSArray *langs) {
    // Line-buffer stdout (defensive)
    setvbuf(stdout, NULL, _IOLBF, 0);

    char buf[1024];
    while (fgets(buf, sizeof(buf), stdin)) {
        // Any non-empty line triggers a capture
        // Trim whitespace:
        char *p = buf;
        while (*p == ' ' || *p == '\t' || *p == '\r' || *p == '\n') ++p;
        if (*p == '\0') continue;
        if (!strncasecmp(p, "quit", 4) || !strncasecmp(p, "exit", 4)) break;

        (void)CaptureAndMaybeEmitJSON(langs, YES);
    }
}

int main(int argc, const char * argv[]) {
    @autoreleasepool {
        BOOL useServer = NO;
        long loopCount = 1;           // default single shot
        long sleepMS   = 0;

        for (int i=1; i<argc; ++i) {
            if (!strcmp(argv[i], "--server")) {
                useServer = YES;
            } else if (!strcmp(argv[i], "--loop") && i+1 < argc) {
                loopCount = strtol(argv[++i], NULL, 10); // <=0 => infinite
            } else if (!strcmp(argv[i], "--sleep-ms") && i+1 < argc) {
                sleepMS = strtol(argv[++i], NULL, 10);
            }
        }

        NSArray *langs = envLanguageHints();

        if (useServer) {
            server_loop(langs);
            return 0;
        }

        if (loopCount == 1) {
            (void)CaptureAndMaybeEmitJSON(langs, YES);
            return 0;
        }

        // Loop mode (<=0 => infinite)
        const BOOL infinite = (loopCount <= 0);
        long n = 0;
        while (infinite || n < loopCount) {
            (void)CaptureAndMaybeEmitJSON(langs, YES);
            ++n;
            if (sleepMS > 0) {
                struct timespec ts;
                ts.tv_sec  = (time_t)(sleepMS / 1000);
                ts.tv_nsec = (long)((sleepMS % 1000) * 1000000L);
                nanosleep(&ts, NULL);
            }
        }
        return 0;
    }
}
