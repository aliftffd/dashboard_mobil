import React, { useState, useEffect } from 'react';
import { MdFormatAlignJustify, MdOutlineNotificationsActive, MdPerson } from 'react-icons/md';
import axios from 'axios';
import Button from '@mui/material/Button';  // Import Button dari Material UI
import './Header.css';  // Pastikan kamu mengimpor file CSS

function Header({ toggleSidebar }) {
  const [hasNotification, setHasNotification] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState('');
  const [showMessage, setShowMessage] = useState(false);
  const [buttonColor, setButtonColor] = useState('primary');  // State untuk warna button

  useEffect(() => {
    // Simulasi pengecekan data yang melebihi batas yang ditentukan
    const checkData = async () => {
      try {
        const response = await axios.get('http://localhost:5001');
        if (response.data.dataLimitExceeded) {
          setHasNotification(true);
          setNotificationMessage('Data melebihi batas yang diizinkan!');
        } else {
          setHasNotification(false);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        setHasNotification(false);
      }
    };

    checkData();
  }, []);

  const handleNotificationClick = () => {
    setShowMessage(!showMessage);
  };

  const handleButtonClick = () => {
    // Mengubah warna button menjadi hijau
    setButtonColor('success');

    // Kembali ke warna semula setelah 1 detik
    setTimeout(() => {
      setButtonColor('primary');
    }, 1000);
  };

  return (
    <header className='header'>
      <div className='menu-icon'>
        <MdFormatAlignJustify className='icon' onClick={toggleSidebar} />
      </div>
      <div className='header-right'>
        <div className='notification-icon' onClick={handleNotificationClick}>
          <MdOutlineNotificationsActive className='icon' />
          {hasNotification && <span className='notification-dot'></span>}
        </div>
        <MdPerson className='icon person-icon' /> {/* Tambahkan kelas CSS tambahan */}
        {/* Tambahkan Button di sini */}
        <Button variant="contained" color={buttonColor} onClick={handleButtonClick}>
          start
        </Button>
      </div>
      {showMessage && hasNotification && (
        <div className='notification-message'>
          {notificationMessage}
        </div>
      )}
    </header>
  );
}

export default Header;
