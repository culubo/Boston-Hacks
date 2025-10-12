import React, { useState, useEffect } from 'react'
import PixelText from './PixelText'

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

  const handleSubmit = (event) => {
    event.preventDefault()
    handleSaveItem()
  }

  return (
    <div>
      <h1 style={{marginBottom: 6, color: '#253244'}}>My Secret Blocker</h1>
      <p>Manage sensitive information you want to block from view.</p>

      <div className="w-full flex justify-center mt-2">
        <label htmlFor="secretInput" className="sr-only">Enter item to block:</label>
        <form onSubmit={handleSubmit} className="w-full max-w-screen-sm">
          <div className="bg-lavender rounded-lg px-3 py-2 flex items-center gap-2 mt-1 justify-center">
            <input
              type="text"
              id="secretInput"
              value={secretItem}
              onChange={handleInputChange}
              placeholder="e.g., API_KEY_123, myPassword"
              className="input-short bg-transparent px-2 py-1 outline-none placeholder-mid-grey"
            />
            <button type="submit" className="save-btn ml-2" aria-label="Save">
              <span className="save-label">Save</span>
            </button>
            <span className="go-label">Go</span>
          </div>
        </form>
      </div>

      <h3 className="mt-4">Blocked Items:</h3>
      {blockedItems.length === 0 ? (
        <p>No items are currently blocked.</p>
      ) : (
        <ul className="blocked-list mt-4">
          {blockedItems.map((item, index) => (
            <li key={index} className="blocked-item">
              <div className="item-text">
                <span className="masked">••••••••</span>
                <span className="reveal">{item}</span>
              </div>
              <button onClick={() => handleDeleteItem(index)} className="delete-btn" aria-label={`Delete item ${index}`}>
                🗑️
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
