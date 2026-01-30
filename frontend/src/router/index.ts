import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import ItemDetailView from '@/views/ItemDetailView.vue'
import NewsView from '@/views/NewsView.vue'
import ResearchView from '@/views/ResearchView.vue'
import PortfolioView from '@/views/PortfolioView.vue'
import AlertsView from '@/views/AlertsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/item/:id',
      name: 'item-detail',
      component: ItemDetailView,
    },
    {
      path: '/news',
      name: 'news',
      component: NewsView,
    },
    {
      path: '/research',
      name: 'research',
      component: ResearchView,
    },
    {
      path: '/portfolio',
      name: 'portfolio',
      component: PortfolioView,
    },
    {
      path: '/alerts',
      name: 'alerts',
      component: AlertsView,
    },
  ],
})

export default router
