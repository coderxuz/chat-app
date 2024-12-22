const socket = new WebSocket("ws://localhost:8000/ws");

socket.onopen = () => {
  socket.send("Hello, WebSocket Server!");
};

socket.onmessage = (event) => {
  console.log("Server says: " + event.data);
};

// Close the WebSocket connection when done
socket.onclose = () => {
  console.log("WebSocket connection closed.");
};