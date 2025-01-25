import React, { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Check, X, AlertCircle, Loader2, ExternalLink } from 'lucide-react';

interface Source {
  id: number;
  name: string;
  url: string;
  type: 'web' | 'rss';
  active: boolean;
  last_scrape: string | null;
}

interface SourceFormData {
  name: string;
  url: string;
  type: 'web' | 'rss';
}

interface RssPreviewItem {
  title: string;
  description: string;
  published: string;
  link: string;
}

interface UrlPreview {
  title: string;
  description: string;
  type: 'web' | 'rss';
  items?: RssPreviewItem[];
  preview_text?: string;
}

export function SourceManager() {
  const [sources, setSources] = useState<Source[]>([]);
  const [isAddingSource, setIsAddingSource] = useState(false);
  const [editingSourceId, setEditingSourceId] = useState<number | null>(null);
  const [formData, setFormData] = useState<SourceFormData>({
    name: '',
    url: '',
    type: 'web'
  });
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<UrlPreview | null>(null);
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);

  useEffect(() => {
    fetchSources();
  }, []);

  const fetchSources = async () => {
    try {
      const response = await fetch('/api/sources');
      if (!response.ok) throw new Error('Falha ao carregar fontes');
      const data = await response.json();
      setSources(data);
    } catch (err) {
      setError('Erro ao carregar fontes');
    }
  };

  const validateUrl = (url: string): string => {
    // Remove any XML/HTML tags
    url = url.replace(/<[^>]*>/g, '');
    // Remove leading/trailing whitespace
    url = url.trim();
    
    try {
      // Try to create a URL object to validate
      new URL(url);
      return url;
    } catch {
      throw new Error('URL inválida');
    }
  };

  const fetchPreview = async (url: string, type: 'web' | 'rss') => {
    setIsLoadingPreview(true);
    setPreviewError(null);
    setPreview(null);

    try {
      const cleanUrl = validateUrl(url);
      const response = await fetch('/api/sources/preview', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: cleanUrl, type }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Falha ao carregar preview');
      }

      const data = await response.json();
      setPreview(data);
      
      // Auto-fill name if empty
      if (!formData.name && data.title) {
        setFormData(prev => ({ ...prev, name: data.title }));
      }
    } catch (err) {
      setPreviewError(err instanceof Error ? err.message : 'Erro ao carregar preview');
    } finally {
      setIsLoadingPreview(false);
    }
  };

  // Debounce the preview fetch
  useEffect(() => {
    const timer = setTimeout(() => {
      if (formData.url && formData.type) {
        fetchPreview(formData.url, formData.type);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [formData.url, formData.type]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      const cleanUrl = validateUrl(formData.url);
      
      const response = await fetch('/api/sources', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          url: cleanUrl
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Falha ao adicionar fonte');
      }

      await fetchSources();
      setIsAddingSource(false);
      setFormData({ name: '', url: '', type: 'web' });
      setPreview(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao adicionar fonte');
    }
  };

  const handleUpdate = async (sourceId: number, data: Partial<Source>) => {
    try {
      if (data.url) {
        data.url = validateUrl(data.url);
      }

      const response = await fetch(`/api/sources/${sourceId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Falha ao atualizar fonte');
      }

      await fetchSources();
      setEditingSourceId(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao atualizar fonte');
    }
  };

  const handleDelete = async (sourceId: number) => {
    if (!window.confirm('Tem certeza que deseja excluir esta fonte?')) return;

    try {
      const response = await fetch(`/api/sources/${sourceId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Falha ao excluir fonte');
      }

      await fetchSources();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao excluir fonte');
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError(null);
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Gerenciar Fontes</h2>
        {!isAddingSource && (
          <button
            onClick={() => setIsAddingSource(true)}
            className="flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            <Plus className="h-5 w-5 mr-2" />
            Adicionar Fonte
          </button>
        )}
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center text-red-700">
          <AlertCircle className="h-5 w-5 mr-2" />
          {error}
        </div>
      )}

      {isAddingSource && (
        <div className="mb-6 p-4 border rounded-lg bg-gray-50">
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                  Nome
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  required
                  value={formData.name}
                  onChange={handleInputChange}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
                  placeholder="Nome da fonte"
                />
              </div>
              <div>
                <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-1">
                  URL
                </label>
                <input
                  type="text"
                  id="url"
                  name="url"
                  required
                  value={formData.url}
                  onChange={handleInputChange}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
                  placeholder="https://..."
                />
              </div>
              <div>
                <label htmlFor="type" className="block text-sm font-medium text-gray-700 mb-1">
                  Tipo
                </label>
                <select
                  id="type"
                  name="type"
                  value={formData.type}
                  onChange={handleInputChange}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
                >
                  <option value="web">Web</option>
                  <option value="rss">RSS</option>
                </select>
              </div>
            </div>

            {/* Preview Section */}
            {formData.url && (
              <div className="mt-4 p-4 bg-white border rounded-lg">
                <h3 className="text-sm font-medium text-gray-700 mb-2">Preview</h3>
                
                {isLoadingPreview && (
                  <div className="flex items-center justify-center py-4 text-gray-500">
                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                    Carregando preview...
                  </div>
                )}

                {previewError && (
                  <div className="text-sm text-red-600">
                    <AlertCircle className="h-4 w-4 inline mr-1" />
                    {previewError}
                  </div>
                )}

                {preview && (
                  <div className="space-y-3">
                    <div>
                      <h4 className="font-medium">{preview.title}</h4>
                      <p className="text-sm text-gray-600">{preview.description}</p>
                    </div>

                    {preview.type === 'rss' && preview.items && (
                      <div className="mt-3">
                        <h5 className="text-sm font-medium text-gray-700 mb-2">Últimas publicações:</h5>
                        <div className="space-y-2">
                          {preview.items.map((item, index) => (
                            <div key={index} className="text-sm">
                              <a
                                href={item.link}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="font-medium text-purple-600 hover:text-purple-900 flex items-center"
                              >
                                {item.title}
                                <ExternalLink className="h-3 w-3 ml-1" />
                              </a>
                              <p className="text-gray-600 text-xs mt-1">{item.published}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {preview.type === 'web' && preview.preview_text && (
                      <div className="mt-3">
                        <h5 className="text-sm font-medium text-gray-700 mb-2">Conteúdo:</h5>
                        <p className="text-sm text-gray-600">{preview.preview_text}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            <div className="mt-4 flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => {
                  setIsAddingSource(false);
                  setFormData({ name: '', url: '', type: 'web' });
                  setError(null);
                  setPreview(null);
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="px-4 py-2 text-sm font-medium text-white bg-purple-600 border border-transparent rounded-md hover:bg-purple-700"
              >
                Adicionar
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Nome
              </th>
              <th className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                URL
              </th>
              <th className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Tipo
              </th>
              <th className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Última Atualização
              </th>
              <th className="px-6 py-3 bg-gray-50"></th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sources.map((source) => (
              <tr key={source.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {editingSourceId === source.id ? (
                    <input
                      type="text"
                      value={formData.name}
                      onChange={handleInputChange}
                      name="name"
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
                    />
                  ) : (
                    source.name
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {editingSourceId === source.id ? (
                    <input
                      type="text"
                      value={formData.url}
                      onChange={handleInputChange}
                      name="url"
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
                    />
                  ) : (
                    <a href={source.url} target="_blank" rel="noopener noreferrer" className="text-purple-600 hover:text-purple-900 flex items-center">
                      {source.url}
                      <ExternalLink className="h-3 w-3 ml-1" />
                    </a>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {editingSourceId === source.id ? (
                    <select
                      value={formData.type}
                      onChange={handleInputChange}
                      name="type"
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
                    >
                      <option value="web">Web</option>
                      <option value="rss">RSS</option>
                    </select>
                  ) : (
                    source.type.toUpperCase()
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {source.last_scrape ? new Date(source.last_scrape).toLocaleString('pt-BR') : 'Nunca'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex justify-end space-x-3">
                    {editingSourceId === source.id ? (
                      <>
                        <button
                          onClick={() => handleUpdate(source.id, formData)}
                          className="text-green-600 hover:text-green-900"
                        >
                          <Check className="h-5 w-5" />
                        </button>
                        <button
                          onClick={() => {
                            setEditingSourceId(null);
                            setFormData({ name: '', url: '', type: 'web' });
                          }}
                          className="text-gray-600 hover:text-gray-900"
                        >
                          <X className="h-5 w-5" />
                        </button>
                      </>
                    ) : (
                      <>
                        <button
                          onClick={() => {
                            setEditingSourceId(source.id);
                            setFormData({
                              name: source.name,
                              url: source.url,
                              type: source.type
                            });
                          }}
                          className="text-purple-600 hover:text-purple-900"
                        >
                          <Edit2 className="h-5 w-5" />
                        </button>
                        <button
                          onClick={() => handleDelete(source.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <Trash2 className="h-5 w-5" />
                        </button>
                      </>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
