import React, { useState, useEffect } from 'react'

export default function PasswordBlocker() {
  const [secretItem, setSecretItem] = useState('')
  const [blockedItems, setBlockedItems] = useState([])

  useEffect(() => {
    const savedItems = localStorage.getItem('blockedItems')
    if (savedItems) {
      setBlockedItems(JSON.parse(savedItems))
    }
  }, [])

  const handleInputChange = (event) => {
    setSecretItem(event.target.value)
  }

  const handleSaveItem = () => {
    if (secretItem.trim() === '') {
      alert('Please enter an item to block.')
      return
    }

    if (!blockedItems.includes(secretItem.trim())) {
      const updatedItems = [...blockedItems, secretItem.trim()]
      setBlockedItems(updatedItems)
      localStorage.setItem('blockedItems', JSON.stringify(updatedItems))
    } else {
      alert('This item is already in your blocked list!')
    }

    setSecretItem('')
  }

  const handleDeleteItem = (indexToDelete) => {
    const updatedItems = blockedItems.filter((_, index) => index !== indexToDelete)
    setBlockedItems(updatedItems)
    localStorage.setItem('blockedItems', JSON.stringify(updatedItems))
  }

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
        <button onClick={handleSaveItem}>Save Item</button>
      </div>

      <h3>Blocked Items:</h3>
      {blockedItems.length === 0 ? (
        <p>No items are currently blocked.</p>
      ) : (
        <ul>
          {blockedItems.map((item, index) => (
            <li key={index}>
              {item}
              <button onClick={() => handleDeleteItem(index)} style={{ marginLeft: '10px' }}>
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
