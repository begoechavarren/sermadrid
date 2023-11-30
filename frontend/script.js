async function getItem() {
    const datetimeInput = document.getElementById('datetimeInput');
    const latitudeInput = document.getElementById('latitudeInput');
    const longitudeInput = document.getElementById('longitudeInput');
    const itemResult = document.getElementById('itemResult');

    try {
        const location = `${latitudeInput.value}${longitudeInput.value}`;
        const response = await fetch(`http://localhost:8080/items/datetime/${datetimeInput.value}/latitude/${latitudeInput.value}/longitude/${longitudeInput.value}`);
        if (!response.ok) {
            itemResult.textContent = 'No response was obtained';
            return;
        }
        const data = await response.json();
        itemResult.textContent = `For the datetime ${datetimeInput.value} and location lat: ${latitudeInput.value} and long: ${longitudeInput.value}, the parking availability is: ${data.result}`;
    } catch (error) {
        console.error('Error fetching availability:', error);
        itemResult.textContent = 'Error fetching availability';
    }
}
