import React, { useEffect } from 'react';
import { RouterProvider } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { RootState } from './Redux/Store/Index';
import Router from './Routes/Index';

const App: React.FC = () => {
  const theme = useSelector((state: RootState) => state.theme.mode);

  useEffect(() => {
    document.body.className = theme === 'dark' ? 'dark bg-black text-white' : 'bg-gray-100 text-black';
  }, [theme]);

  return (
    <>  
      <RouterProvider router={Router} />
    </>
  );
};

export default App;
