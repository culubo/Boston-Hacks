import React, { useState, useEffect } from 'react'; // 1. Import useEffect

function PasswordBlocker() {
  const [secretItem, setSecretItem] = useState('');
  // 2. State to hold all the stored secret items (passwords/API keys)
  const [blockedItems, setBlockedItems] = useState([]);

  // 3. useEffect to load items from localStorage when the component first mounts
  useEffect(() => {
    const savedItems = localStorage.getItem('blockedItems'); // Try to get items from localStorage
    if (savedItems) {
      // If items exist, parse them from string back to array and set state
      setBlockedItems(JSON.parse(savedItems));
    }
  }, []); // The empty dependency array [] ensures this runs only once, like componentDidMount

  const handleInputChange = (event) => {
    setSecretItem(event.target.value);
  };

  // 4. Function to handle saving a new item
  const handleSaveItem = () => {
    if (secretItem.trim() === '') { // Prevent saving empty strings
      alert('Please enter an item to block.');
      return;
    }

    // Create a new array with the existing items plus the new one
    // We also check to avoid duplicates
    if (!blockedItems.includes(secretItem.trim())) {
        const updatedItems = [...blockedItems, secretItem.trim()];
        setBlockedItems(updatedItems); // Update React state
        // Save the updated array to localStorage (must be stringified)
        localStorage.setItem('blockedItems', JSON.stringify(updatedItems));
    } else {
        alert('This item is already in your blocked list!');
    }


    setSecretItem(''); // Clear the input field after saving
  };

  // 5. Function to handle deleting an item
  const handleDeleteItem = (indexToDelete) => {
    // Filter out the item at the specified index
    const updatedItems = blockedItems.filter((_, index) => index !== indexToDelete);
    setBlockedItems(updatedItems); // Update React state
    // Save the updated array to localStorage
    localStorage.setItem('blockedItems', JSON.stringify(updatedItems));
  };


  return (
    <div>
      <h1>My Secret Blocker</h1>
      <p>Manage sensitive information you want to block from view.</p>

      <div>
        <label htmlFor="secretInput">Enter item to block:</label>
        <input
          type="text"
          id="secretInput"
          value={secretItem}
          onChange={handleInputChange}
          placeholder="e.g., API_KEY_123, myPassword"
        />
        {/* 6. The Save button */}
        <button onClick={handleSaveItem}>Save Item</button>
      </div>

      {/* 7. Display the list of blocked items */}
      <h3>Blocked Items:</h3>
      {blockedItems.length === 0 ? (
        <p>No items are currently blocked.</p>
      ) : (
        <ul>
          {blockedItems.map((item, index) => (
            <li key={index}> {/* Using index as key is okay for simple, non-reorderable lists */}
              {item}
              {/* 8. Delete button for each item */}
              <button onClick={() => handleDeleteItem(index)} style={{ marginLeft: '10px' }}>
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default PasswordBlocker;