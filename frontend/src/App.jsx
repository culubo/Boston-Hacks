import './App.css';
import PasswordBlocker from './features/UserBlocker/PasswordBlocker';
import Header from './components/Header';
import Footer from './components/Footer';

function App() {
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

export default App;
