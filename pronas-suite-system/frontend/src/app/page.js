// src/app/page.js
import Link from 'next/link';

// Mock de dados de projetos
const projects = [
  { id: 1, name: 'Projeto de Fisioterapia Pediátrica', status: 'Aprovado' },
  { id: 2, name: 'Centro de Reabilitação Visual', status: 'Em Análise' },
  { id: 3, name: 'Oficina de Próteses', status: 'Reprovado' },
];

export default function Dashboard() {
  return (
    <div className="container mx-auto p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Dashboard de Projetos</h1>
        <Link href="/projects/new">
          <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
            + Novo Projeto
          </button>
        </Link>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">Meus Projetos</h2>
        <ul>
          {projects.map((project) => (
            <li key={project.id} className="flex justify-between items-center border-b py-2">
              <span>{project.name}</span>
              <span className={`px-3 py-1 text-sm rounded-full ${
                project.status === 'Aprovado' ? 'bg-green-200 text-green-800' :
                project.status === 'Em Análise' ? 'bg-yellow-200 text-yellow-800' :
                'bg-red-200 text-red-800'
              }`}>
                {project.status}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
