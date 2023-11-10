async function getItem() {
    const itemIdInput = document.getElementById('itemIdInput');
    const itemResult = document.getElementById('itemResult');
    try {
        // TODO: Parameterize the URL
        const response = await fetch(`http://localhost:8080/items/${itemIdInput.value}`);
        if (!response.ok) {
            itemResult.textContent = 'No response was obtained';
            return;
        }
        const data = await response.json();
        itemResult.textContent = data.item_id; // Display only the item_id
    } catch (error) {
        console.error('Error fetching item:', error);
        itemResult.textContent = 'Error fetching item';
    }
}
