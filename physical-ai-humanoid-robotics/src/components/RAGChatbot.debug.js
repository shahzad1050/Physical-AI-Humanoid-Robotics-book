// Debug: Check if RAGChatbot loads properly
console.log('RAGChatbot component loaded');

// Check API connectivity on page load
const checkAPI = async () => {
  const apiUrl = (typeof window !== 'undefined' && window.NEXT_PUBLIC_API_BASE_URL)
    ? window.NEXT_PUBLIC_API_BASE_URL
    : 'http://localhost:8000';
  try {
    const response = await fetch(`${apiUrl}/health`);
    console.log('API Health Check:', response.status === 200 ? 'CONNECTED' : 'ERROR');
  } catch (err) {
    console.warn('API not reachable:', err);
  }
};

if (typeof window !== 'undefined') {
  checkAPI();
}
