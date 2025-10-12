import PasswordBlocker from '../src/components/PasswordBlocker'
import Header from '../src/components/Header'
import Footer from '../src/components/Footer'

export default function Home() {
  return (
    <div className="App">
      <Header>
        <div className="card">
          <PasswordBlocker />
        </div>
      </Header>
      <Footer />
    </div>
  )
}
