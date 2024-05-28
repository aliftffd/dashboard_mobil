import React, { useState } from 'react'
import { Link } from 'react-router-dom';
import { MdOutlineSpeed, MdHistory, MdQuestionMark, MdTrain, MdLocationOn, MdClose } from 'react-icons/md'

function Sidebar({ openSidebarToggle, toggleSidebar }) {
    return (
        <aside id="Sidebar" className={openSidebarToggle ? "sidebar sidebar-open" : "sidebar"}>
            <div className='sidebar-title'>
                <div className='sidebar-brand'>
                    <MdTrain className='icon_header' /> ATP
                </div>
                <div className='icon close_icon' onClick={toggleSidebar}>
                    <MdClose />
                </div>
            </div>

            <ul className='sidebar-list'>
                <li className='sidebar-list-item'>
                    <Link to="/" onClick={toggleSidebar}>
                        <MdOutlineSpeed className='icon' /> Dashboard
                    </Link>
                </li>
                <li className='sidebar-list-item'>
                    <Link to="/History" onClick={toggleSidebar}>
                        <MdHistory className='icon' /> History
                    </Link>
                </li>
            </ul>
        </aside>
    )
}

export default Sidebar