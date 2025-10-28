import React from 'react';

// Define styles as objects for inline use
const textLabelStyle: React.CSSProperties = {
  fontFamily: 'Arial, Helvetica, sans-serif',
  fontSize: '18px',
  fontWeight: 'bold',
  fill: '#E0E0E0', // Changed to light grey
  textAnchor: 'middle',
};

const arrowStyle: React.CSSProperties = {
  fill: '#E0E0E0', // Changed to light grey
  stroke: '#E0E0E0', // Changed to light grey
  strokeWidth: 1.5,
};

const PdfToMdLogoDark: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 100 120" // Keeps the icon's aspect ratio
    width="24" // Default width from your example
    height="24" // Default height from your example
    aria-label="PDF to Markdown conversion logo (dark theme)"
    {...props} // Spreads props like className, onClick, etc.
  >
    {/* Main document shape outline and fold */}
    <defs>
      <path
        id="doc-shape-dark"
        d="M10 10 L70 10 L90 30 L90 110 L10 110 Z"
        stroke="#9E9E9E" // Lighter border for dark theme
        strokeWidth="3"
        strokeLinejoin="round"
      />
      <path
        id="fold-shape-dark"
        d="M70 10 L90 30 L70 30 Z"
        stroke="#9E9E9E" // Lighter border for dark theme
        strokeWidth="3"
        strokeLinejoin="round"
      />
    </defs>

    {/* Left Side (PDF) */}
    <g>
      <path
        d="M10 10 L50 10 L50 110 L10 110 Z"
        fill="#555555" // Replaced red with medium-dark grey
      />
      <text style={textLabelStyle} x="30" y="70">
        PDF
      </text>
    </g>

    {/* Right Side (MD) */}
    <g>
      <path
        d="M50 10 L70 10 L90 30 L90 110 L50 110 Z"
        fill="#222222" // Kept dark, slightly darker
      />
      <text style={textLabelStyle} x="70" y="70">
        MD
      </text>
    </g>

    {/* Conversion Arrow (on the divider) */}
    <g style={arrowStyle}>
      <line x1="50" y1="45" x2="50" y2="75" />
      <polygon points="45 55, 55 65, 45 75" />
    </g>

    {/* Apply the main outline over everything */}
    <use href="#doc-shape-dark" fill="none" />
    <use href="#fold-shape-dark" fill="none" />
  </svg>
);

export default PdfToMdLogoDark;