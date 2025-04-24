import { useState, useCallback } from 'react';

interface UsePaginationProps {
  initialPage?: number;
  totalPages: number;
}

interface UsePaginationReturn {
  currentPage: number;
  goToPage: (page: number) => void;
  nextPage: () => void;
  previousPage: () => void;
}

export const usePagination = ({
  initialPage = 1,
  totalPages,
}: UsePaginationProps): UsePaginationReturn => {
  const [currentPage, setCurrentPage] = useState(initialPage);

  const goToPage = useCallback((page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  }, [totalPages]);

  const nextPage = useCallback(() => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  }, [currentPage, totalPages]);

  const previousPage = useCallback(() => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  }, [currentPage]);

  return {
    currentPage,
    goToPage,
    nextPage,
    previousPage,
  };
}; 