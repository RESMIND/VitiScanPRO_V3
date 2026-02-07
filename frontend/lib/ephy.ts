import { api } from './api';

export interface EphyProductSummary {
  numero_amm: string;
  nom_produit: string;
  titulaire: string;
  fonctions: string;
  etat_produit: string;
  type_produit: string;
  type_commercial: string;
  gamme_usage: string;
  mentions_autorisees: string;
  substances_actives: string;
}

export interface EphyUsage {
  identifiant_usage: string;
  etat_usage: string;
  dose: string;
  dose_unite: string;
  delai_avant_recolte_jour: string;
  delai_avant_recolte_bbch: string;
  nombre_max_applications: string;
  intervalle_min_jour: string;
  date_decision: string;
  date_fin_distribution: string;
  date_fin_utilisation: string;
  condition_emploi: string;
  znt_aquatique: string;
  znt_arthropodes: string;
  znt_plantes: string;
  mentions_autorisees: string;
}

export interface EphyProductDetail {
  product: EphyProductSummary & {
    formulations: string;
    reference_amm: string;
    reference_nom: string;
  };
  usages: EphyUsage[];
}

export const ephyAPI = {
  search: async (query: string, limit = 20, etat = 'AUTORISE') => {
    const response = await api.get('/api/ephy/products/search', {
      params: { q: query, limit, etat },
    });
    return response.data as { query: string; count: number; results: EphyProductSummary[] };
  },

  getProduct: async (amm: string) => {
    const response = await api.get(`/api/ephy/products/${amm}`);
    return response.data as EphyProductDetail;
  },

  status: async () => {
    const response = await api.get('/api/ephy/status');
    return response.data as {
      last_update: string;
      products_count: number;
      usages_count: number;
      viticulture_only: boolean;
    };
  },
};
