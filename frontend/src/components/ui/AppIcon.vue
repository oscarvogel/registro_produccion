<template>
  <component
    :is="iconComponent"
    :class="sizeClass"
    :stroke-width="strokeWidth"
    :aria-hidden="title ? undefined : 'true'"
    :aria-label="title || undefined"
    role="img"
  />
</template>

<script setup>
import { computed } from 'vue'
import {
  AlertTriangle,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  ArrowUp,
  BookOpen,
  Boxes,
  Building2,
  CheckCircle,
  ChevronDown,
  CircleHelp,
  ClipboardList,
  Cloud,
  Download,
  Eye,
  EyeOff,
  Factory,
  Fuel,
  Gauge,
  Home,
  Layers,
  Leaf,
  ListChecks,
  LoaderCircle,
  LogIn,
  LogOut,
  Map,
  MapPin,
  Menu,
  MoreVertical,
  Moon,
  Pencil,
  Play,
  Plus,
  RefreshCw,
  RotateCcw,
  Save,
  Search,
  Settings,
  ShieldCheck,
  Sprout,
  Sun,
  Timer,
  Trash2,
  TreePine,
  Truck,
  UserRound,
  Users,
  Wifi,
  WifiOff,
  X,
} from 'lucide-vue-next'

const props = defineProps({
  name: { type: String, required: true },
  size: { type: String, default: 'md' },
  strokeWidth: { type: Number, default: 2 },
  title: { type: String, default: '' },
})

const icons = {
  home: Home,
  production: Factory,
  pending: Cloud,
  records: ClipboardList,
  dashboard: Gauge,
  admin: ShieldCheck,
  settings: Settings,
  logout: LogOut,
  refresh: RefreshCw,
  add: Plus,
  edit: Pencil,
  delete: Trash2,
  save: Save,
  close: X,
  back: ArrowLeft,
  forward: ArrowRight,
  filter: ListChecks,
  sync: RefreshCw,
  retry: RotateCcw,
  view: Eye,
  hide: EyeOff,
  forest: TreePine,
  leaf: Leaf,
  unit: Building2,
  process: Layers,
  truck: Truck,
  machine: Truck,
  fuel: Fuel,
  location: MapPin,
  field: Map,
  plot: Sprout,
  personnel: Users,
  person: UserRound,
  assignment: ClipboardList,
  success: CheckCircle,
  warning: AlertTriangle,
  error: AlertTriangle,
  offline: WifiOff,
  online: Wifi,
  empty: Boxes,
  download: Download,
  play: Play,
  timer: Timer,
  search: Search,
  menu: Menu,
  more: MoreVertical,
  moon: Moon,
  chevronDown: ChevronDown,
  arrowUp: ArrowUp,
  arrowDown: ArrowDown,
  loading: LoaderCircle,
  login: LogIn,
  manual: BookOpen,
  sun: Sun,
}

const sizes = {
  xs: 'h-3 w-3',
  sm: 'h-4 w-4',
  md: 'h-5 w-5',
  lg: 'h-6 w-6',
  xl: 'h-8 w-8',
}

const iconComponent = computed(() => icons[props.name] || CircleHelp)
const sizeClass = computed(() => sizes[props.size] || sizes.md)
</script>
