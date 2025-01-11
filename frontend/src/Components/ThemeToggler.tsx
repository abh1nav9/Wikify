import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../Redux/Store/Index';
import { toggleTheme } from '../Redux/Slice/ThemeSlice';

const ThemeToggler: React.FC = () => {
    const dispatch = useDispatch();
    const theme = useSelector((state: RootState) => state.theme.mode);
  
    return (
      <button
        onClick={() => dispatch(toggleTheme())}
        className={`p-2 rounded ${theme === 'dark' ? 'bg-black text-white' : 'bg-gray-200 text-black'}`}
      >
        Toggle Theme
      </button>
    );
  };
  
  export default ThemeToggler;