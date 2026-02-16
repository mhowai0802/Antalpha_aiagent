import type { Page } from '../App';
import type { LucideIcon } from 'lucide-react';
import { MessageSquare, Wallet, ArrowLeftRight, GitBranch, X, User } from 'lucide-react';
import './Sidebar.scss';

interface Props {
  activePage: Page;
  onNavigate: (page: Page) => void;
  open: boolean;
  onClose: () => void;
}

const items: { id: Page; label: string; icon: LucideIcon }[] = [
  { id: 'chat', label: 'Chat', icon: MessageSquare },
  { id: 'wallet', label: 'Wallet', icon: Wallet },
  { id: 'transactions', label: 'Transactions', icon: ArrowLeftRight },
  { id: 'architecture', label: 'How It Works', icon: GitBranch },
];

const USER_ID = 'user_default';

export default function Sidebar({ activePage, onNavigate, open, onClose }: Props) {
  return (
    <div className={`sidebar ${open ? 'sidebar--open' : ''}`}>
      <div className="sidebar-logo">
        <div className="sidebar-logo__title">Crypto Agent</div>
        <div className="sidebar-logo__subtitle">Simulated Trading</div>
        <button className="sidebar-logo__close" onClick={onClose}>
          <X size={16} />
        </button>
      </div>
      <nav className="sidebar-nav">
        {items.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => onNavigate(id)}
            className={`sidebar-nav__item ${activePage === id ? 'sidebar-nav__item--active' : ''}`}
          >
            <Icon size={18} className="sidebar-nav__icon" />
            {label}
          </button>
        ))}
      </nav>
      <div className="sidebar-user">
        <User size={16} className="sidebar-user__icon" />
        <span className="sidebar-user__id">{USER_ID}</span>
      </div>
    </div>
  );
}
