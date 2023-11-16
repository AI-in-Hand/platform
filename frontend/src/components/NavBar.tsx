import Link from 'next/link';
import React from 'react';

const NavBar: React.FC = () => {
  return (
    <nav className="flex justify-between items-center p-4 bg-blue-500 text-white">
      <span className="font-bold">My AI Project</span>
      <div>
        <Link href="/">
          <a className="p-2">Home</a>
        </Link>
        <Link href="/dashboard">
          <a className="p-2">Dashboard</a>
        </Link>
        {/* Add more links as needed */}
      </div>
    </nav>
  );
};

export default NavBar;
