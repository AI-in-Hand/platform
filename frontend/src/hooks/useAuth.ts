import { useState, useEffect } from 'react';
import { auth } from '../services/firebase'; // Import Firebase auth service

const useAuth = () => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged(setUser);
    return () => unsubscribe();
  }, []);

  return { user };
};

export default useAuth;
