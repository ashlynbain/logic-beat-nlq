/** Tiny pixel sprites — no image assets needed */

export function PixelFlower({ className = "", color = "pink" }: { className?: string; color?: "pink" | "yellow" | "purple" }) {
  const petal =
    color === "yellow" ? "#ffe066" : color === "purple" ? "#c9a0ff" : "#ff8fab";
  const center = color === "yellow" ? "#ffb347" : "#fff5a0";

  return (
    <svg
      className={`pixel-sprite ${className}`}
      width="32"
      height="32"
      viewBox="0 0 8 8"
      shapeRendering="crispEdges"
      aria-hidden
    >
      <rect x="3" y="0" width="2" height="2" fill={petal} />
      <rect x="1" y="2" width="2" height="2" fill={petal} />
      <rect x="5" y="2" width="2" height="2" fill={petal} />
      <rect x="0" y="4" width="2" height="2" fill={petal} />
      <rect x="6" y="4" width="2" height="2" fill={petal} />
      <rect x="2" y="4" width="4" height="2" fill={center} />
      <rect x="3" y="6" width="2" height="2" fill="#5cb85c" />
    </svg>
  );
}

export function PixelHeart({ className = "" }: { className?: string }) {
  return (
    <svg
      className={`pixel-sprite ${className}`}
      width="24"
      height="24"
      viewBox="0 0 8 8"
      shapeRendering="crispEdges"
      aria-hidden
    >
      <rect x="1" y="1" width="2" height="2" fill="#ff6b9d" />
      <rect x="5" y="1" width="2" height="2" fill="#ff6b9d" />
      <rect x="0" y="2" width="8" height="2" fill="#ff6b9d" />
      <rect x="0" y="4" width="8" height="2" fill="#ff6b9d" />
      <rect x="1" y="6" width="6" height="1" fill="#ff6b9d" />
      <rect x="2" y="7" width="4" height="1" fill="#ff6b9d" />
    </svg>
  );
}

export function PixelStar({ className = "" }: { className?: string }) {
  return (
    <svg
      className={`pixel-sprite ${className}`}
      width="20"
      height="20"
      viewBox="0 0 8 8"
      shapeRendering="crispEdges"
      aria-hidden
    >
      <rect x="3" y="0" width="2" height="2" fill="#fff5a0" />
      <rect x="1" y="2" width="6" height="2" fill="#fff5a0" />
      <rect x="0" y="3" width="2" height="2" fill="#fff5a0" />
      <rect x="6" y="3" width="2" height="2" fill="#fff5a0" />
      <rect x="2" y="4" width="4" height="2" fill="#fff5a0" />
      <rect x="3" y="6" width="2" height="2" fill="#fff5a0" />
    </svg>
  );
}

export function MeadowScene() {
  return (
    <div className="meadow-scene" aria-hidden>
      <div className="cloud cloud-a" />
      <div className="cloud cloud-b" />
      <div className="grass-strip" />
      <PixelFlower className="deco-flower f1" color="pink" />
      <PixelFlower className="deco-flower f2" color="yellow" />
      <PixelFlower className="deco-flower f3" color="purple" />
      <PixelFlower className="deco-flower f4" color="pink" />
      <PixelFlower className="deco-flower f5" color="yellow" />
      <PixelHeart className="deco-heart h1" />
      <PixelHeart className="deco-heart h2" />
      <PixelStar className="deco-star s1" />
      <PixelStar className="deco-star s2" />
    </div>
  );
}
