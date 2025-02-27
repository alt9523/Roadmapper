// Handles all API communication
class DataService {
  async fetchData() {
    try {
      const response = await fetch('/api/data');
      if (!response.ok) {
        throw new Error('Failed to fetch data');
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching data:', error);
      throw error;
    }
  }

  async saveData(data) {
    try {
      const response = await fetch('/api/data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      
      if (!response.ok) {
        throw new Error('Failed to save data');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error saving data:', error);
      throw error;
    }
  }
}

export default new DataService(); 