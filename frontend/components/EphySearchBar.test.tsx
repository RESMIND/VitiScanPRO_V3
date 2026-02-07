import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect } from 'vitest';

import EphySearchBar from './EphySearchBar';

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
  },
}));

describe('EphySearchBar', () => {
  it('shows dropdown results', async () => {
    render(<EphySearchBar />);

    const input = screen.getByPlaceholderText('Recherche e-Phy (AMM ou nom)');
    fireEvent.change(input, { target: { value: 'prod' } });

    await waitFor(() => {
      expect(screen.getByText('Produit Vigne')).toBeInTheDocument();
    });
  });
});
