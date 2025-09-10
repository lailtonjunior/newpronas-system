// src/app/page.js
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

// Mock de dados
const projects = [
  { id: 1, name: 'Projeto de Fisioterapia Pediátrica', status: 'Aprovado' },
  { id: 2, name: 'Centro de Reabilitação Visual', status: 'Em Análise' },
  { id: 3, name: 'Oficina de Próteses', status: 'Reprovado' },
];

const getStatusClass = (status) => {
  switch (status) {
    case 'Aprovado':
      return 'bg-green-100 text-green-800';
    case 'Em Análise':
      return 'bg-yellow-100 text-yellow-800';
    case 'Reprovado':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

export default function Dashboard() {
  return (
    <div className="container mx-auto p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Dashboard de Projetos</h1>
        <Link href="/projects/new" passHref>
          <Button>+ Novo Projeto com IA</Button>
        </Link>
      </div>

      <Card>
        <h2 className="text-xl font-semibold mb-4 text-gray-700">Meus Projetos</h2>
        <ul className="space-y-2">
          {projects.map((project) => (
            <li key={project.id} className="flex justify-between items-center border-b py-3">
              <span className="font-medium text-gray-600">{project.name}</span>
              <span className={`px-3 py-1 text-sm rounded-full font-semibold ${getStatusClass(project.status)}`}>
                {project.status}
              </span>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}