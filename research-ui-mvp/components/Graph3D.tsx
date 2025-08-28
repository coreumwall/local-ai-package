import dynamic from 'next/dynamic';
import { useEffect, useState } from 'react';

const ForceGraph3D = dynamic(() => import('react-force-graph-3d'), { ssr: false });

export default function Graph3D({ initialData }: { initialData?: any }) {
  const [data, setData] = useState(initialData || { nodes:[], links:[] });

  // Minimal demo data if none provided
  useEffect(() => {
    if (!initialData) {
      setData({
        nodes:[{id:'Topic:A'},{id:'Doc:1'},{id:'Claim:X'}],
        links:[{source:'Topic:A', target:'Doc:1'},{source:'Doc:1',target:'Claim:X'}]
      });
    }
  }, [initialData]);

  return (
    <ForceGraph3D
      graphData={data}
      enableNodeDrag={false}
      onNodeClick={(n:any) => alert(n.id)}
    />
  );
}
