import React, { useEffect, useState } from "react";
import API_URL from "./config";
function App() {
  const [products, setProducts] = useState([]);
  useEffect(() => {
    fetch(`${API_URL}/products`)
      .then(res => res.json())
      .then(data => setProducts(data))
      .catch(err => console.error("Erreur API:", err));
  }, []);
  return (
    <div>
      <h1>Liste des produits</h1>
      <ul>
        {products.map(p => (
          <li key={p.id}>
            {p.name} — {p.price} FCFA
          </li>
        ))}
      </ul>
    </div>
  );
}
export default App;
