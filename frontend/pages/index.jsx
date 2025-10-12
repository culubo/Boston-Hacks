import PasswordBlocker from '../src/components/PasswordBlocker'
import Header from '../src/components/Header'
import LearnLink from '../src/components/LearnLink'

export default function Home() {
  return (
    <div className="App">
      <Header>
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <PasswordBlocker />
        <LearnLink />
      </Header>
    </div>
  )
}
