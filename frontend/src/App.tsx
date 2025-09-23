import './App.css'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import ChatPage from './pages/ChatPage'

function App() {
  return (
    <Router>
      <Routes>
        <Route path='/' element={<ChatPage />}></Route>
        <Route path='*' element={<h1>404 - Not found page</h1>}></Route>
      </Routes>
    </Router>
  )
}

export default App
