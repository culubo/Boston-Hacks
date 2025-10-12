import random
import string

def generate_fake_api_keys():
    def fake_aws_access_key():
        # 20 chars starting with 'AKIA'
        return 'AKIA' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

    def fake_aws_secret_key():
        # 40 chars, mix of letters, digits, '/', '+'
        chars = string.ascii_letters + string.digits + '/+'
        return ''.join(random.choices(chars, k=40))

    def fake_google_api_key():
        # starts with 'AIza' + 35 alphanumeric chars
        return 'AIza' + ''.join(random.choices(string.ascii_letters + string.digits, k=35))

    def fake_stripe_key():
        # starts with 'sk_test_' + 24 alphanumeric chars
        return 'sk_test_' + ''.join(random.choices(string.ascii_letters + string.digits, k=24))

    def fake_github_token():
        # 40 hex chars starting with 'ghp_'
        hex_chars = string.hexdigits.lower()
        return 'ghp_' + ''.join(random.choices(hex_chars, k=36))

    def fake_generic_api_key():
        # 32 alphanumeric chars
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

    return {
        'aws_access_key': fake_aws_access_key(),
        'aws_secret_key': fake_aws_secret_key(),
        'google_api_key': fake_google_api_key(),
        'stripe_key': fake_stripe_key(),
        'github_token': fake_github_token(),
        'generic_api_key': fake_generic_api_key()
    }

# Example usage:
if __name__ == "__main__":
    keys = generate_fake_api_keys()
    for k, v in keys.items():
        print(f"{k}: {v}")