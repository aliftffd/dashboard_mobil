import { useState } from 'react'
import './App.css'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './header/Header'
import Sidebar from './sidebar/Sidebar'
import Home from './Home'
import History from './History'

function App() {
  const [openSidebarToggle, setOpenSidebarToggle] = useState(false)

  const toggleSidebar = () => {
    setOpenSidebarToggle(!openSidebarToggle)
  }

  return (
    <Router>
      <div className={`grid-container ${openSidebarToggle ? 'sidebar-open' : ''}`}>
        <Header toggleSidebar={toggleSidebar} />
        <Sidebar openSidebarToggle={openSidebarToggle} toggleSidebar={toggleSidebar} />
        <main className='content'>
          <Routes>
            <Route path="/" element={<Home />} />  {/* Rute untuk halaman utama */}
            <Route path="/History" element={<History />} />  {/* Rute untuk halaman History */}
          </Routes>
        </main>
      </div>
    </Router>
  );
}
export default App
