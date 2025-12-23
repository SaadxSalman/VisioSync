import { Canvas } from '@react-three/fiber'
import { OrbitControls, Environment } from '@react-three/drei'
import { DigitalHuman } from '../components/Avatar/DigitalHuman'

export default function Page() {
  // In a real app, this state would be updated by your tRPC mutation results
  const [currentExpression, setCurrentExpression] = React.useState('happy')

  return (
    <main className="h-screen w-full bg-slate-900">
      <Canvas camera={{ position: [0, 0, 5], fov: 45 }}>
        <ambientLight intensity={0.5} />
        <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} />
        <Environment preset="city" />
        
        <React.Suspense fallback={null}>
          <DigitalHuman expression={currentExpression} influence={0.8} />
        </React.Suspense>
        
        <OrbitControls enableZoom={false} />
      </Canvas>
      
      {/* Your Camera/Chat UI overlays here */}
    </main>
  )
}