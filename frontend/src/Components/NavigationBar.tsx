import React from 'react';
import ThemeToggler from './ThemeToggler';

const NavigationBar: React.FC = () => {
  return (
    <>
      <div className="flex justify-between items-center p-4">
        <div className="text-xl font-bold text-gray-800 dark:text-white">
          Wikify
        </div>
        <div>
          <ThemeToggler />
        </div>
      </div>
    </>
  );
};

export default NavigationBar;
