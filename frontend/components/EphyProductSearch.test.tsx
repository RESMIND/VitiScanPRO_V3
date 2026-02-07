import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';

import EphyProductSearch from './EphyProductSearch';

vi.mock('@/lib/ephy', () => ({
  ephyAPI: {
    search: vi.fn(async () => ({
      query: 'prod',
      count: 1,
      results: [
        {
          numero_amm: '123456',
          nom_produit: 'Produit Vigne',
          titulaire: 'Titulaire A',
          fonctions: 'Fongicide',
          etat_produit: 'AUTORISE',
          type_produit: 'PPP',
          type_commercial: 'Type X',
          gamme_usage: 'Usage X',
          mentions_autorisees: '',
          substances_actives: 'Substance A',
        },
      ],
    })),
    getProduct: vi.fn(async () => ({
      product: {
        numero_amm: '123456',
        nom_produit: 'Produit Vigne',
        titulaire: 'Titulaire A',
        fonctions: 'Fongicide',
        etat_produit: 'AUTORISE',
        type_produit: 'PPP',
        type_commercial: 'Type X',
        gamme_usage: 'Usage X',
        mentions_autorisees: '',
        substances_actives: 'Substance A',
        formulations: 'WP',
        reference_amm: '',
        reference_nom: '',
      },
      usages: [
        {
          identifiant_usage: 'Vigne*Trt Part.Aer.*Mildiou(s)',
          etat_usage: 'AUTORISE',
          dose: '2.5',
          dose_unite: 'kg/ha',
          delai_avant_recolte_jour: '21',
          delai_avant_recolte_bbch: '',
          nombre_max_applications: '3',
          intervalle_min_jour: '',
          date_decision: '2025-01-01',
          date_fin_distribution: '',
          date_fin_utilisation: '',
          condition_emploi: '',
          znt_aquatique: '20',
          znt_arthropodes: '5',
          znt_plantes: '',
          mentions_autorisees: '',
        },
      ],
    })),
  },
}));

describe('EphyProductSearch', () => {
  it('renders search results and loads product detail', async () => {
    render(<EphyProductSearch />);

    const input = screen.getByPlaceholderText('Rechercher un produit (AMM ou nom)');
    fireEvent.change(input, { target: { value: 'prod' } });

    await waitFor(() => {
      expect(screen.getByText('Produit Vigne')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Produit Vigne'));

    await waitFor(() => {
      expect(screen.getByText('Usages viticoles: 1')).toBeInTheDocument();
    });
  });
});
