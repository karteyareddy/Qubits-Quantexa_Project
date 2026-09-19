const pageStyle = {
  alignItems: "center",
  background: "#07111f",
  color: "#e5eef8",
  display: "flex",
  fontFamily: "Arial, sans-serif",
  justifyContent: "center",
  minHeight: "100vh",
  padding: "2rem",
} as const;

const cardStyle = {
  background: "#0e1b2d",
  border: "1px solid #24364d",
  borderRadius: "1rem",
  maxWidth: "36rem",
  padding: "3rem",
  textAlign: "center",
  width: "100%",
} as const;

export default function Home() {
  return (
    <main style={pageStyle}>
      <section style={cardStyle}>
        <h1>Quantum Traffic Optimizer</h1>
        <p>Stage 1 Skeleton</p>
        <p>Backend: FastAPI</p>
        <p>Frontend: Next.js</p>
      </section>
    </main>
  );
}
