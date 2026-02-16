import { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  themeVariables: {
    primaryColor: '#333',
    primaryTextColor: '#ddd',
    primaryBorderColor: '#555',
    lineColor: '#888',
    secondaryColor: '#252525',
    tertiaryColor: '#1e1e1e',
    background: '#1e1e1e',
    mainBkg: '#252525',
    nodeBorder: '#555',
    clusterBkg: '#2a2a2a',
    clusterBorder: '#444',
    titleColor: '#ddd',
    edgeLabelBackground: '#1e1e1e',
    actorBkg: '#252525',
    actorBorder: '#555',
    actorTextColor: '#ddd',
    actorLineColor: '#555',
    signalColor: '#ddd',
    signalTextColor: '#ddd',
    noteBkgColor: '#333',
    noteTextColor: '#ddd',
    noteBorderColor: '#555',
  },
  flowchart: { curve: 'basis', padding: 16 },
  sequence: { mirrorActors: false },
});

let idCounter = 0;

interface Props {
  chart: string;
}

export default function Mermaid({ chart }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState('');

  useEffect(() => {
    let cancelled = false;
    const id = `mermaid-${idCounter++}`;

    mermaid.render(id, chart).then(({ svg: rendered }) => {
      if (!cancelled) setSvg(rendered);
    }).catch((err) => {
      console.error('Mermaid render error:', err);
    });

    return () => { cancelled = true; };
  }, [chart]);

  return (
    <div
      ref={containerRef}
      className="mermaid-diagram"
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}
