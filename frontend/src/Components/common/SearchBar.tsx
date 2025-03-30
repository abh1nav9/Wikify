function SearchBar() {
  return (
    <div className="flex justify-center items-center p-4 gap-4">
      <input
        type="text"
        placeholder="Search WIki"
        className="px-3 py-2 rounded-full border border-gray-300 focus:outline-none dark:bg-gray-800 dark:text-white dark:border-gray-600"
      />
      <button className="px-4 py-2 rounded-full border border-gray-300 bg-gray-200 text-black hover:bg-gray-300 focus:outline-none dark:bg-gray-700 dark:text-white dark:border-gray-600 dark:hover:bg-gray-600">
        Search
      </button>
    </div>
  );
}

export default SearchBar;
