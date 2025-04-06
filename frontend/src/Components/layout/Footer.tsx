import React from "react";
import { FaGithub, FaLinkedin } from "react-icons/fa";
import { MdEmail } from "react-icons/md";

const Footer: React.FC = () => {
  return (
    <footer className="w-full border-t border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-4 py-6 flex flex-col sm:flex-row justify-between items-center text-sm text-gray-600 dark:text-gray-400">
        <p className="mb-2 sm:mb-0">Made with <span className="text-red-500">♥</span> by Abhinav</p>
        
        <div className="flex space-x-5 text-xl">
          <a
            href="https://linkedin.com/in/iabhinavgautam"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
            aria-label="LinkedIn"
          >
            <FaLinkedin />
          </a>
          <a
            href="https://github.com/abh1nav9"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-gray-800 dark:hover:text-white transition-colors"
            aria-label="GitHub"
          >
            <FaGithub />
          </a>
          <a
            href="mailto:abhinavgautam092@email.com"
            className="hover:text-red-600 dark:hover:text-red-400 transition-colors"
            aria-label="Email"
          >
            <MdEmail />
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
