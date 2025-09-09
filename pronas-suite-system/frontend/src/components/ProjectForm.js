'use client';
import { useForm } from 'react-hook-form';
import { Input } from './ui/Input';
import { Button } from './ui/Button';

export function ProjectForm({ project, onSave }) {
    const { register, handleSubmit, formState: { errors } } = useForm({
        defaultValues: project || { title: '', description: '', status: 'Em Análise', institution_id: '' },
    });

    const onSubmit = (data) => {
        onSave(data);
    };

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
                <label htmlFor="title" className="block text-sm font-medium text-gray-700">Título do Projeto</label>
                <Input
                    id="title"
                    {...register('title', { required: 'Título é obrigatório' })}
                />
                {errors.title && <p className="text-red-500 text-xs mt-1">{errors.title.message}</p>}
            </div>
            <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700">Descrição</label>
                <textarea
                    id="description"
                    rows={5}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    {...register('description')}
                />
            </div>
             <div>
                <label htmlFor="institution_id" className="block text-sm font-medium text-gray-700">ID da Instituição</label>
                <Input
                    id="institution_id"
                    type="number"
                    {...register('institution_id', { required: 'ID da instituição é obrigatório' })}
                />
                 {errors.institution_id && <p className="text-red-500 text-xs mt-1">{errors.institution_id.message}</p>}
            </div>
            <div className="flex justify-end">
                <Button type="submit">Salvar Projeto</Button>
            </div>
        </form>
    );
}