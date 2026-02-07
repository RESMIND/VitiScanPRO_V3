import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-6xl font-bold text-green-800 mb-6">
            VitiScan v3
          </h1>
          <p className="text-2xl text-green-700 mb-8">
            Gestion intelligente des vignobles
          </p>
          <p className="text-lg text-gray-700 mb-12">
            Surveillez vos domaines, parcelles et cultures avec une technologie IA avancée. 
            Scannez et analysez la santé des plantes pour des décisions éclairées.
          </p>
          
          <div className="flex gap-4 justify-center">
            <Link 
              href="/login"
              className="bg-green-600 hover:bg-green-700 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-colors"
            >
              Connexion
            </Link>
            <Link 
              href="/register"
              className="bg-white hover:bg-gray-50 text-green-600 border-2 border-green-600 px-8 py-4 rounded-lg text-lg font-semibold transition-colors"
            >
              S'inscrire
            </Link>
          </div>

          <div className="mt-16 grid md:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-4xl mb-4">🌿</div>
              <h3 className="text-xl font-semibold text-green-800 mb-2">Gestion du Domaine</h3>
              <p className="text-gray-600">Gérez plusieurs domaines et parcelles depuis un seul endroit</p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-4xl mb-4">📸</div>
              <h3 className="text-xl font-semibold text-green-800 mb-2">Scans IA</h3>
              <p className="text-gray-600">Détectez les maladies et problèmes avec l'intelligence artificielle</p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-xl font-semibold text-green-800 mb-2">Analyses Détaillées</h3>
              <p className="text-gray-600">Rapports et statistiques pour des décisions éclairées</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
