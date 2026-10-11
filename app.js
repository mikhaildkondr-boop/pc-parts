// PickMyPC - Interactive Application Logic with Multi-Country Real Market Pricing & Used Hardware Deals
// Supported Countries: Ukraine (UAH), Italy (EUR), USA (USD), Germany (EUR), UK (GBP), France (EUR), Spain (EUR), Europe (EUR)
// Condition Support: Brand New Retail & Used / Refurbished Deals (OLX, Subito, eBay, Kleinanzeigen, CeX, etc.)
// Strict Exclusion: Russia is not included.

document.addEventListener('DOMContentLoaded', () => {
  // Application State
  const state = {
    selectedParts: {},
    partConditions: JSON.parse(localStorage.getItem('pickmypc_conditions') || '{}'),
    country: localStorage.getItem('pickmypc_country') || 'US',
    globalCondition: localStorage.getItem('pickmypc_global_cond') || 'all',
    modalCondition: 'all',
    activeCategory: null,
    searchFilter: '',
    maxPrice: 2500,
    selectedBrands: new Set(),
    hideIncompatible: true,
    theme: localStorage.getItem('pickmypc_theme') || 'theme-light'
  };

  // Initialize theme
  document.body.className = state.theme;
  updateThemeIcon();

  // Toast notification feedback helper
  function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type === 'success' ? 'toast-success' : (type === 'warning' ? 'toast-warning' : '')}`;

    let iconName = 'info';
    if (type === 'success') iconName = 'check-circle';
    else if (type === 'warning') iconName = 'alert-triangle';

    toast.innerHTML = `
      <div class="toast-icon"><i data-lucide="${iconName}"></i></div>
      <div class="toast-message">${escapeHtml(message)}</div>
    `;

    container.appendChild(toast);
    lucide.createIcons();

    setTimeout(() => {
      toast.style.animation = 'toastFadeOut 0.25s forwards';
      setTimeout(() => {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
      }, 250);
    }, 3200);
  }

  // Helper functions for localized prices, condition, and currency
  function getCountryConfig(code = state.country) {
    if (typeof COUNTRIES !== 'undefined' && COUNTRIES[code]) {
      return COUNTRIES[code];
    }
    return {
      code: 'US',
      name: 'United States',
      flag: '🇺🇸',
      currency: 'USD',
      symbol: '$',
      position: 'prefix',
      rate: 1.0,
      merchants: ['Amazon', 'Newegg', 'Best Buy', 'Micro Center'],
      usedMerchants: ['eBay (Pre-Owned)', 'r/hardwareswap', 'Jawa.gg'],
      defaultShipping: 'FREE Shipping',
      marketNote: 'US MSRP / Street prices (excl. sales tax)'
    };
  }

  function getLocalizedPartData(part, code = state.country, condition = 'new') {
    if (!part) return null;
    const countryData = (part.country_prices && part.country_prices[code]) ? part.country_prices[code] : null;

    if (countryData) {
      if (condition === 'used') {
        return {
          price: countryData.used_price,
          currency: countryData.currency,
          symbol: countryData.symbol,
          merchant: countryData.used_merchant,
          shipping: countryData.used_shipping,
          savings: countryData.used_savings,
          savings_pct: countryData.used_savings_pct,
          condition: 'used'
        };
      }
      return {
        price: countryData.price,
        currency: countryData.currency,
        symbol: countryData.symbol,
        merchant: countryData.merchant,
        shipping: countryData.shipping,
        savings: 0,
        savings_pct: 0,
        condition: 'new'
      };
    }

    // Fallback if no country map
    const basePrice = condition === 'used' ? roundVal(part.price * 0.68) : part.price;
    return {
      price: basePrice,
      currency: 'USD',
      symbol: '$',
      merchant: condition === 'used' ? 'eBay (Pre-Owned)' : part.merchant,
      shipping: condition === 'used' ? 'Buyer Protected Shipping' : 'FREE Shipping',
      savings: condition === 'used' ? roundVal(part.price - basePrice) : 0,
      savings_pct: condition === 'used' ? 32 : 0,
      condition: condition
    };
  }

  function roundVal(num) {
    return Math.round(num * 100) / 100;
  }

  function formatCurrency(amount, code = state.country) {
    const cfg = getCountryConfig(code);
    if (cfg.currency === 'UAH') {
      return `${Math.round(amount).toLocaleString('uk-UA')} ₴`;
    } else if (cfg.currency === 'EUR') {
      return `€${amount.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    } else if (cfg.currency === 'GBP') {
      return `£${amount.toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    } else {
      return `$${amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }
  }

  function updateCountryBanner() {
    const cfg = getCountryConfig(state.country);
    const flagEl = document.getElementById('countryMarketFlag');
    const textEl = document.getElementById('countryMarketText');
    if (flagEl) flagEl.textContent = cfg.flag;
    if (textEl) {
      const topStores = cfg.merchants ? cfg.merchants.slice(0, 3).join(', ') : '';
      const topUsed = cfg.usedMerchants ? cfg.usedMerchants.slice(0, 2).join(', ') : '';
      textEl.innerHTML = `Region: <strong>${escapeHtml(cfg.name)}</strong> • Retail: ${escapeHtml(topStores)} | Used: ${escapeHtml(topUsed)}`;
    }
  }

  function adjustPriceFilterForCountry() {
    const cfg = getCountryConfig(state.country);
    const slider = document.getElementById('priceRangeSlider');
    const label = document.getElementById('priceRangeValue');
    if (!slider || !label) return;

    if (cfg.currency === 'UAH') {
      slider.min = 500;
      slider.max = 120000;
      slider.step = 500;
      state.maxPrice = 120000;
      slider.value = 120000;
      label.textContent = `${slider.value.toLocaleString()} ₴`;
    } else if (cfg.currency === 'GBP') {
      slider.min = 20;
      slider.max = 2500;
      slider.step = 10;
      state.maxPrice = 2500;
      slider.value = 2500;
      label.textContent = `£${slider.value}`;
    } else if (cfg.currency === 'EUR') {
      slider.min = 20;
      slider.max = 2800;
      slider.step = 10;
      state.maxPrice = 2800;
      slider.value = 2800;
      label.textContent = `€${slider.value}`;
    } else {
      slider.min = 20;
      slider.max = 2500;
      slider.step = 10;
      state.maxPrice = 2500;
      slider.value = 2500;
      label.textContent = `$${slider.value}`;
    }
  }

  function updatePresetPrices() {
    if (typeof PRESET_BUILDS === 'undefined') return;

    Object.entries(PRESET_BUILDS).forEach(([key, preset]) => {
      let sum = 0;
      const isUsedPreset = (key === 'used_budget');
      Object.values(preset.parts).forEach(partId => {
        const found = PARTS_DATABASE.find(p => p.id === partId);
        if (found) {
          const partData = getLocalizedPartData(found, state.country, isUsedPreset ? 'used' : 'new');
          sum += partData.price;
        }
      });

      const formatted = formatCurrency(sum, state.country);

      // Dynamic updates for all presets
      const el = document.getElementById(`showcasePrice_${key}`);
      if (el) el.textContent = formatted;
      const drop = document.getElementById(`dropPrice_${key}`);
      if (drop) drop.textContent = `~${formatted}`;

      // Legacy element fallbacks
      if (key === 'used_budget') {
        const elOld = document.getElementById('showcasePriceUsedBudget');
        if (elOld) elOld.textContent = formatted;
        const dropOld = document.getElementById('dropPriceUsedBudget');
        if (dropOld) dropOld.textContent = `~${formatted}`;
      } else if (key === 'budget_1080p' || key === 'budget') {
        const elOld = document.getElementById('showcasePriceBudget');
        if (elOld) elOld.textContent = formatted;
        const dropOld = document.getElementById('dropPriceBudget');
        if (dropOld) dropOld.textContent = `~${formatted}`;
      } else if (key === 'midrange') {
        const elOld = document.getElementById('showcasePriceMidrange');
        if (elOld) elOld.textContent = formatted;
        const elHigh = document.getElementById('showcasePrice_high_preset');
        if (elHigh) elHigh.textContent = formatted;
        const dropOld = document.getElementById('dropPriceMidrange');
        if (dropOld) dropOld.textContent = `~${formatted}`;
      } else if (key === 'enthusiast') {
        const elOld = document.getElementById('showcasePriceEnthusiast');
        if (elOld) elOld.textContent = formatted;
        const elUltra = document.getElementById('showcasePrice_ultra_preset');
        if (elUltra) elUltra.textContent = formatted;
        const dropOld = document.getElementById('dropPriceEnthusiast');
        if (dropOld) dropOld.textContent = `~${formatted}`;
      }
    });
  }

  function setCountry(code) {
    if (!COUNTRIES || !COUNTRIES[code]) return;
    state.country = code;
    localStorage.setItem('pickmypc_country', code);

    const countrySelect = document.getElementById('countrySelect');
    if (countrySelect && countrySelect.value !== code) {
      countrySelect.value = code;
    }

    updateCountryBanner();
    adjustPriceFilterForCountry();
    updatePresetPrices();
    renderBuilderTable();
    updateDiagnosticsAndTotals();

    const partPickerModal = document.getElementById('partPickerModal');
    if (partPickerModal && partPickerModal.classList.contains('active')) {
      renderCatalogResults();
    }

    lucide.createIcons();
  }

  // Country Selector Event Listener
  const countrySelect = document.getElementById('countrySelect');
  if (countrySelect) {
    countrySelect.value = state.country;
    countrySelect.addEventListener('change', (e) => {
      setCountry(e.target.value);
      const cfg = getCountryConfig(e.target.value);
      showToast(`Region updated: ${cfg.flag} ${cfg.name} (${cfg.currency})`, 'success');
    });
  }

  // Global Condition Selector
  const conditionSelect = document.getElementById('conditionSelect');
  if (conditionSelect) {
    conditionSelect.value = state.globalCondition;
    conditionSelect.addEventListener('change', (e) => {
      state.globalCondition = e.target.value;
      localStorage.setItem('pickmypc_global_cond', state.globalCondition);

      // If user sets global condition to 'used' or 'new', update selected components to match
      if (state.globalCondition === 'used') {
        Object.keys(state.selectedParts).forEach(cat => {
          state.partConditions[cat] = 'used';
        });
      } else if (state.globalCondition === 'new') {
        Object.keys(state.selectedParts).forEach(cat => {
          state.partConditions[cat] = 'new';
        });
      }
      saveBuildState();
      renderBuilderTable();
      updateDiagnosticsAndTotals();
      lucide.createIcons();

      const labels = { all: 'All Parts (New & Used)', new: 'Brand New Retail', used: 'Used & Refurbished' };
      showToast(`Condition: ${labels[state.globalCondition] || state.globalCondition}`, 'info');
    });
  }

  // Modal Condition Filter Pills
  const modalConditionPills = document.getElementById('modalConditionPills');
  if (modalConditionPills) {
    modalConditionPills.querySelectorAll('.cond-pill').forEach(btn => {
      btn.addEventListener('click', () => {
        modalConditionPills.querySelectorAll('.cond-pill').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.modalCondition = btn.dataset.cond;
        renderCatalogResults();
      });
    });
  }

  // Toggle single component condition (New <-> Used)
  window.togglePartCondition = function(categoryId) {
    const part = state.selectedParts[categoryId];
    const current = state.partConditions[categoryId] || 'new';
    const next = current === 'used' ? 'new' : 'used';
    state.partConditions[categoryId] = next;
    saveBuildState();
    renderBuilderTable();
    updateDiagnosticsAndTotals();
    lucide.createIcons();

    if (part) {
      const nextLabel = next === 'used' ? 'Pre-Owned Deal (Savings Applied!)' : 'Brand New Retail';
      showToast(`Switched ${part.name} to ${nextLabel}`, 'success');
    }
  };

  // Load saved build from localStorage if the user previously selected parts
  const savedBuild = localStorage.getItem('pickmypc_build');
  if (savedBuild) {
    try {
      const parsed = JSON.parse(savedBuild);
      Object.entries(parsed).forEach(([cat, id]) => {
        const found = PARTS_DATABASE.find(p => p.id === id);
        if (found) state.selectedParts[cat] = found;
      });
    } catch (e) {
      console.error('Failed to parse saved build', e);
    }
  }
  // If no saved build, start completely empty so the user builds their own system from scratch

  // Initial UI Render
  updateCountryBanner();
  adjustPriceFilterForCountry();
  updatePresetPrices();
  renderBuilderTable();
  updateDiagnosticsAndTotals();
  lucide.createIcons();

  // =========================================================================
  // Event Listeners
  // =========================================================================

  // Theme toggle
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  themeToggleBtn.addEventListener('click', () => {
    state.theme = state.theme === 'theme-dark' ? 'theme-light' : 'theme-dark';
    document.body.className = state.theme;
    localStorage.setItem('pickmypc_theme', state.theme);
    updateThemeIcon();
    showToast(state.theme === 'theme-dark' ? 'Dark theme enabled' : 'Light theme enabled', 'info');
  });

  // Preset build dropdown
  const presetMenuBtn = document.getElementById('presetMenuBtn');
  const presetDropdown = document.getElementById('presetDropdown');
  presetMenuBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    presetDropdown.classList.toggle('show');
  });

  document.addEventListener('click', () => {
    presetDropdown.classList.remove('show');
  });

  presetDropdown.querySelectorAll('.dropdown-item').forEach(item => {
    item.addEventListener('click', (e) => {
      e.stopPropagation();
      const presetKey = item.dataset.preset;
      presetDropdown.classList.remove('show');
      applyPreset(presetKey);
    });
  });

  // Clear list
  const clearBuildBtn = document.getElementById('clearBuildBtn');
  clearBuildBtn.addEventListener('click', () => {
    if (confirm('Are you sure you want to clear your current part list?')) {
      state.selectedParts = {};
      state.partConditions = {};
      saveBuildState();
      renderBuilderTable();
      updateDiagnosticsAndTotals();
      lucide.createIcons();
      showToast('Cleared all parts from list', 'info');
    }
  });

  // Modal Close buttons
  const partPickerModal = document.getElementById('partPickerModal');
  const modalCloseBtn = document.getElementById('modalCloseBtn');
  modalCloseBtn.addEventListener('click', closeModal);
  partPickerModal.addEventListener('click', (e) => {
    if (e.target === partPickerModal) closeModal();
  });

  // Modal Filters
  const globalSearch = document.getElementById('globalSearch');
  if (globalSearch) {
    globalSearch.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && globalSearch.value.trim()) {
        const query = globalSearch.value.trim().toLowerCase();
        const match = PARTS_DATABASE.find(p => p.name.toLowerCase().includes(query) || p.brand.toLowerCase().includes(query));
        const cat = match ? match.category : 'cpu';
        openPickerModal(cat);
        partSearchInput.value = globalSearch.value;
        state.searchFilter = query;
        renderCatalogResults();
      }
    });
  }

  const partSearchInput = document.getElementById('partSearchInput');
  partSearchInput.addEventListener('input', (e) => {
    state.searchFilter = e.target.value.toLowerCase();
    renderCatalogResults();
  });

  const priceRangeSlider = document.getElementById('priceRangeSlider');
  const priceRangeValue = document.getElementById('priceRangeValue');
  priceRangeSlider.addEventListener('input', (e) => {
    state.maxPrice = Number(e.target.value);
    const cfg = getCountryConfig(state.country);
    if (cfg.currency === 'UAH') {
      priceRangeValue.textContent = `${state.maxPrice.toLocaleString()} ₴`;
    } else if (cfg.currency === 'GBP') {
      priceRangeValue.textContent = `£${state.maxPrice}`;
    } else if (cfg.currency === 'EUR') {
      priceRangeValue.textContent = `€${state.maxPrice}`;
    } else {
      priceRangeValue.textContent = `$${state.maxPrice}`;
    }
    renderCatalogResults();
  });

  const compatFilterOnly = document.getElementById('compatFilterOnly');
  compatFilterOnly.addEventListener('change', (e) => {
    state.hideIncompatible = e.target.checked;
    renderCatalogResults();
  });

  const resetFiltersBtn = document.getElementById('resetFiltersBtn');
  resetFiltersBtn.addEventListener('click', () => {
    state.searchFilter = '';
    partSearchInput.value = '';
    adjustPriceFilterForCountry();
    state.selectedBrands.clear();
    state.hideIncompatible = true;
    compatFilterOnly.checked = true;
    state.modalCondition = 'all';
    if (modalConditionPills) {
      modalConditionPills.querySelectorAll('.cond-pill').forEach(b => {
        b.classList.toggle('active', b.dataset.cond === 'all');
      });
    }
    populateBrandFilters();
    renderCatalogResults();
    showToast('Filters reset to default', 'info');
  });

  // Share / Export Modal
  const shareBuildBtn = document.getElementById('shareBuildBtn');
  const exportModal = document.getElementById('exportModal');
  const exportModalCloseBtn = document.getElementById('exportModalCloseBtn');
  const copyExportBtn = document.getElementById('copyExportBtn');
  const exportTextArea = document.getElementById('exportTextArea');
  const copyNotification = document.getElementById('copyNotification');
  let currentExportTab = 'reddit';

  shareBuildBtn.addEventListener('click', () => {
    updateExportText();
    exportModal.classList.add('active');
    lucide.createIcons();
  });

  exportModalCloseBtn.addEventListener('click', () => {
    exportModal.classList.remove('active');
    copyNotification.textContent = '';
  });

  exportModal.addEventListener('click', (e) => {
    if (e.target === exportModal) {
      exportModal.classList.remove('active');
      copyNotification.textContent = '';
    }
  });

  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentExportTab = btn.dataset.tab;
      updateExportText();
    });
  });

  copyExportBtn.addEventListener('click', () => {
    exportTextArea.select();
    exportTextArea.setSelectionRange(0, 99999);

    const onCopySuccess = () => {
      copyNotification.textContent = '✓ Copied to clipboard!';
      showToast('Build export copied to clipboard!', 'success');
      setTimeout(() => { copyNotification.textContent = ''; }, 3000);
    };

    const fallbackCopy = () => {
      try {
        const successful = document.execCommand('copy');
        if (successful) {
          onCopySuccess();
        } else {
          copyNotification.textContent = 'Please press Ctrl+C to copy.';
        }
      } catch (err) {
        copyNotification.textContent = 'Please press Ctrl+C to copy.';
      }
    };

    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(exportTextArea.value)
        .then(onCopySuccess)
        .catch(fallbackCopy);
    } else {
      fallbackCopy();
    }
  });

  // Navigation Links Smooth Scroll & Active Tracking
  const navLinks = document.querySelectorAll('.nav-link');
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      const href = link.getAttribute('href');
      if (href && href.startsWith('#')) {
        e.preventDefault();
        navLinks.forEach(l => l.classList.remove('active'));
        link.classList.add('active');
        if (href === '#' || href === '#partsTable') {
          const table = document.getElementById('partsTable');
          if (table) table.scrollIntoView({ behavior: 'smooth', block: 'start' });
          else window.scrollTo({ top: 0, behavior: 'smooth' });
        } else {
          const target = document.querySelector(href);
          if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }
      }
    });
  });

  const brandLogo = document.querySelector('.brand-logo');
  if (brandLogo) {
    brandLogo.addEventListener('click', (e) => {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
      navLinks.forEach(l => l.classList.remove('active'));
      const sbLink = document.getElementById('navSystemBuilder');
      if (sbLink) sbLink.classList.add('active');
    });
  }

  // Keyboard Escape Key Handler for Modals & Dropdowns
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (partPickerModal && partPickerModal.classList.contains('active')) {
        closeModal();
      }
      if (exportModal && exportModal.classList.contains('active')) {
        exportModal.classList.remove('active');
        copyNotification.textContent = '';
      }
      if (presetDropdown && presetDropdown.classList.contains('show')) {
        presetDropdown.classList.remove('show');
      }
    }
  });

  // Footer Links Interactive Feedback
  document.querySelectorAll('.footer-links a').forEach(a => {
    a.addEventListener('click', (e) => {
      e.preventDefault();
      const text = a.textContent.trim();
      if (text.includes('Privacy')) {
        showToast('Privacy: PickMyPC is 100% client-side. No trackers, no cookies.', 'info');
      } else if (text.includes('Terms')) {
        showToast('Terms: Free and open-source system builder tool.', 'info');
      } else {
        showToast('Hardware Database: 278 real PC parts across 8 countries.', 'info');
      }
    });
  });

  // =========================================================================
  // Core Compatibility Engine
  // =========================================================================
  function runCompatibilityCheck() {
    const issues = [];
    const notes = [];
    const { cpu, cooler, motherboard, memory, gpu, case: pcCase, psu } = state.selectedParts;

    // 1. CPU vs Motherboard Socket
    if (cpu && motherboard) {
      if (cpu.specs.socket !== motherboard.specs.socket) {
        issues.push(`Incompatibility: The ${cpu.name} (Socket ${cpu.specs.socket}) is not compatible with ${motherboard.name} (Socket ${motherboard.specs.socket}).`);
      } else {
        notes.push(`Motherboard & CPU share compatible socket (${cpu.specs.socket}).`);
      }
    }

    // 2. Motherboard vs RAM type (DDR4 vs DDR5)
    if (motherboard && memory) {
      if (motherboard.specs.ramType !== memory.specs.type) {
        issues.push(`Incompatibility: The ${motherboard.name} requires ${motherboard.specs.ramType} memory, but ${memory.name} is ${memory.specs.type}.`);
      } else {
        notes.push(`RAM specification matches motherboard memory standard (${memory.specs.type}).`);
      }
    }

    // 3. Motherboard Form Factor vs Case
    if (motherboard && pcCase) {
      if (pcCase.specs.supportedMobos && !pcCase.specs.supportedMobos.includes(motherboard.specs.formFactor)) {
        issues.push(`Incompatibility: The ${pcCase.name} does not fit ${motherboard.specs.formFactor} motherboards (supports: ${pcCase.specs.supportedMobos.join(', ')}).`);
      } else {
        notes.push(`Motherboard form factor (${motherboard.specs.formFactor}) fits within the chosen case.`);
      }
    }

    // 4. GPU Length vs Case Max GPU Length
    if (gpu && pcCase) {
      if (gpu.specs.lengthMm && pcCase.specs.maxGpuLengthMm && gpu.specs.lengthMm > pcCase.specs.maxGpuLengthMm) {
        issues.push(`Warning: The GPU length (${gpu.specs.lengthMm}mm) exceeds the maximum GPU clearance for ${pcCase.name} (${pcCase.specs.maxGpuLengthMm}mm).`);
      }
    }

    // 5. Estimated Wattage & PSU Capacity
    const hasAnyParts = Object.values(state.selectedParts).some(p => Boolean(p));
    let totalWattage = hasAnyParts ? 50 : 0;
    if (cpu && cpu.specs.tdp) totalWattage += cpu.specs.tdp;
    if (gpu && gpu.specs.tdp) totalWattage += gpu.specs.tdp;
    if (memory) totalWattage += 15;
    if (state.selectedParts.storage) totalWattage += 10;
    if (cooler) totalWattage += 15;

    if (psu) {
      if (psu.specs.wattage < totalWattage) {
        issues.push(`Warning: The estimated system power consumption (${totalWattage}W) exceeds the selected PSU capacity (${psu.specs.wattage}W). A ${totalWattage + 150}W+ PSU is strongly recommended.`);
      } else if (psu.specs.wattage < (totalWattage + 80)) {
        notes.push(`Power note: The selected PSU (${psu.specs.wattage}W) is close to the estimated wattage (${totalWattage}W). Consider a higher wattage for overclocking headroom.`);
      } else {
        notes.push(`PSU (${psu.specs.wattage}W) offers ample headroom for the estimated ${totalWattage}W draw.`);
      }
    }

    return {
      compatible: issues.length === 0,
      issues,
      notes,
      totalWattage
    };
  }

  function isPartCompatible(part) {
    const { cpu, motherboard, memory, case: pcCase } = state.selectedParts;

    if (part.category === 'cpu' && motherboard) {
      if (part.specs.socket !== motherboard.specs.socket) return false;
    }
    if (part.category === 'motherboard') {
      if (cpu && part.specs.socket !== cpu.specs.socket) return false;
      if (memory && part.specs.ramType !== memory.specs.type) return false;
      if (pcCase && pcCase.specs.supportedMobos && !pcCase.specs.supportedMobos.includes(part.specs.formFactor)) return false;
    }
    if (part.category === 'memory' && motherboard) {
      if (part.specs.type !== motherboard.specs.ramType) return false;
    }
    if (part.category === 'case' && motherboard) {
      if (part.specs.supportedMobos && !part.specs.supportedMobos.includes(motherboard.specs.formFactor)) return false;
    }
    return true;
  }

  // =========================================================================
  // UI Rendering Functions
  // =========================================================================

  function renderBuilderTable() {
    const tbody = document.getElementById('partsTableBody');
    tbody.innerHTML = '';

    CATEGORIES.forEach(cat => {
      const part = state.selectedParts[cat.id];
      const tr = document.createElement('tr');

      if (!part) {
        // Empty Slot Row
        tr.className = 'table-row-empty';
        tr.innerHTML = `
          <td class="col-component">
            <div class="component-cell">
              <i data-lucide="${cat.icon}"></i>
              <span>${cat.name}</span>
            </div>
          </td>
          <td class="col-selection">
            <button class="btn btn-choose" onclick="openPickerModal('${cat.id}')">
              <i data-lucide="plus"></i> Choose ${cat.singular}
            </button>
          </td>
          <td class="col-specs"><span class="text-dim">-</span></td>
          <td class="col-price">-</td>
          <td class="col-promo">-</td>
          <td class="col-merchant">-</td>
          <td class="col-total">-</td>
          <td class="col-actions"></td>
        `;
      } else {
        // Populated Slot Row with condition pill & localized price
        const cond = state.partConditions[cat.id] || 'new';
        const loc = getLocalizedPartData(part, state.country, cond);
        const newLoc = getLocalizedPartData(part, state.country, 'new');
        const usedLoc = getLocalizedPartData(part, state.country, 'used');
        const formattedPrice = formatCurrency(loc.price);

        const isUsed = (cond === 'used');
        const condBadgeHtml = isUsed
          ? `<span class="cond-badge cond-used"><i data-lucide="tag"></i> Pre-Owned <span class="used-savings-pill">Save ${usedLoc.savings_pct}%</span></span>`
          : `<span class="cond-badge cond-new"><i data-lucide="sparkles"></i> Brand New</span>`;

        const condToggleBtnHtml = isUsed
          ? `<button class="btn-cond-toggle" onclick="togglePartCondition('${cat.id}')" title="Switch back to brand new retail">✨ Switch to New (${formatCurrency(newLoc.price)})</button>`
          : `<button class="btn-cond-toggle" onclick="togglePartCondition('${cat.id}')" title="Save money with tested pre-owned marketplace deal">♻️ Switch to Used (Save ${formatCurrency(usedLoc.savings)})</button>`;

        tr.className = 'table-row-selected';
        tr.innerHTML = `
          <td class="col-component">
            <div class="component-cell">
              <i data-lucide="${cat.icon}"></i>
              <span>${cat.name}</span>
            </div>
          </td>
          <td class="col-selection">
            <div class="product-item">
              <div class="product-thumb">
                <i data-lucide="${cat.icon}"></i>
              </div>
              <div class="product-info">
                <span class="product-title">${escapeHtml(part.name)}</span>
                <div class="product-rating">
                  <span class="stars-icon"><i data-lucide="star"></i></span>
                  <strong>${part.rating}</strong>
                  <span>(${part.reviews} reviews)</span>
                </div>
                ${condBadgeHtml}
                ${condToggleBtnHtml}
              </div>
            </div>
          </td>
          <td class="col-specs">
            <div class="specs-tag-list">
              <span class="spec-badge">${escapeHtml(part.specs.col1 || '')}</span>
              ${part.specs.col2 ? `<span class="spec-badge">${escapeHtml(part.specs.col2)}</span>` : ''}
            </div>
          </td>
          <td class="col-price">${formattedPrice}</td>
          <td class="col-promo"><span class="spec-badge">${escapeHtml(loc.shipping)}</span></td>
          <td class="col-merchant">
            <span class="merchant-badge"><i data-lucide="shopping-cart"></i> ${escapeHtml(loc.merchant)}</span>
          </td>
          <td class="col-total">${formattedPrice}</td>
          <td class="col-actions">
            <div class="action-buttons-cell">
              <button class="btn btn-sm btn-outline" onclick="openPickerModal('${cat.id}')" title="Change component">Change</button>
              <button class="btn-icon-subtle" onclick="removePart('${cat.id}')" title="Remove part">
                <i data-lucide="trash-2"></i>
              </button>
            </div>
          </td>
        `;
      }
      tbody.appendChild(tr);
    });
  }

  function updateDiagnosticsAndTotals() {
    const check = runCompatibilityCheck();

    // Calculate Total Price in active currency and active condition
    let totalPrice = 0;
    let newPriceTotal = 0;

    Object.entries(state.selectedParts).forEach(([cat, p]) => {
      if (!p) return;
      const cond = state.partConditions[cat] || 'new';
      const loc = getLocalizedPartData(p, state.country, cond);
      const newLoc = getLocalizedPartData(p, state.country, 'new');

      totalPrice += loc.price;
      newPriceTotal += newLoc.price;
    });

    const totalSavings = Math.max(0, newPriceTotal - totalPrice);
    const formattedPrice = formatCurrency(totalPrice);

    document.getElementById('totalPrice').textContent = formattedPrice;
    document.getElementById('tableFooterTotal').textContent = formattedPrice;
    document.getElementById('totalWattage').textContent = `${check.totalWattage} W`;

    // Update Used Savings Card
    const savingsCard = document.getElementById('savingsCard');
    const totalSavingsEl = document.getElementById('totalSavings');
    if (savingsCard && totalSavingsEl) {
      if (totalSavings > 0) {
        const savingsPct = Math.round((totalSavings / newPriceTotal) * 100);
        totalSavingsEl.textContent = `${formatCurrency(totalSavings)} (-${savingsPct}%)`;
        savingsCard.style.display = 'block';
      } else {
        savingsCard.style.display = 'none';
      }
    }

    // Update Compatibility Status Banner
    const badge = document.getElementById('compatStatusBadge');
    const badgeTitle = document.getElementById('compatText');
    const badgeSub = document.getElementById('compatSubtext');
    const badgeIcon = document.getElementById('compatIcon');

    badge.className = 'compat-badge';
    if (check.compatible) {
      badge.classList.add('compat-green');
      badgeTitle.textContent = 'Compatibility: No issues or incompatibilities found.';
      badgeSub.textContent = 'All hardware sockets, memory standards, and form factors are compatible.';
      badgeIcon.setAttribute('data-lucide', 'shield-check');
    } else {
      badge.classList.add('compat-red');
      badgeTitle.textContent = 'Compatibility: Hardware Issues Detected!';
      badgeSub.textContent = `${check.issues.length} conflict(s) found. See details below.`;
      badgeIcon.setAttribute('data-lucide', 'alert-triangle');
    }

    // Notes and Diagnostics List
    const notesList = document.getElementById('compatNotesList');
    notesList.innerHTML = '';

    if (check.issues.length > 0) {
      check.issues.forEach(iss => {
        const li = document.createElement('li');
        li.style.color = '#ef4444';
        li.innerHTML = `<strong>Conflict:</strong> ${escapeHtml(iss)}`;
        notesList.appendChild(li);
      });
    }

    if (totalSavings > 0) {
      const li = document.createElement('li');
      li.style.color = '#10b981';
      li.innerHTML = `<strong>Market Savings:</strong> You are saving <strong>${formatCurrency(totalSavings)}</strong> by choosing tested pre-owned/refurbished components instead of brand new retail!`;
      notesList.appendChild(li);
    }

    check.notes.forEach(note => {
      const li = document.createElement('li');
      li.innerHTML = `<strong>Note:</strong> ${escapeHtml(note)}`;
      notesList.appendChild(li);
    });

    if (notesList.children.length === 0) {
      const li = document.createElement('li');
      li.innerHTML = `<strong>Note:</strong> Select components to run real-time hardware compatibility checks.`;
      notesList.appendChild(li);
    }

    // Update real-world gaming performance benchmarks
    if (window.GamingBenchmarkEngine && typeof window.GamingBenchmarkEngine.update === 'function') {
      window.GamingBenchmarkEngine.update();
    }
  }

  window.getSelectedParts = function() {
    return state.selectedParts;
  };

  // =========================================================================
  // Modal Component Picker
  // =========================================================================

  window.openPickerModal = function(categoryId) {
    state.activeCategory = categoryId;
    const cat = CATEGORIES.find(c => c.id === categoryId);
    if (!cat) return;

    document.getElementById('modalCategoryTitle').textContent = `Choose ${cat.singular}`;
    document.getElementById('modalCategoryIcon').innerHTML = `<i data-lucide="${cat.icon}"></i>`;

    const col1Header = document.getElementById('catalogDynamicCol1');
    const col2Header = document.getElementById('catalogDynamicCol2');
    if (col1Header && col2Header) {
      if (categoryId === 'cpu') {
        col1Header.textContent = 'Cores / Speed';
        col2Header.textContent = 'TDP / Socket';
      } else if (categoryId === 'gpu') {
        col1Header.textContent = 'VRAM / Memory';
        col2Header.textContent = 'Boost Clock / TDP';
      } else if (categoryId === 'motherboard') {
        col1Header.textContent = 'Socket / Chipset';
        col2Header.textContent = 'Form Factor / RAM';
      } else if (categoryId === 'memory') {
        col1Header.textContent = 'Speed / Type';
        col2Header.textContent = 'Modules / CAS';
      } else if (categoryId === 'storage') {
        col1Header.textContent = 'Capacity / Interface';
        col2Header.textContent = 'Form Factor / Speed';
      } else if (categoryId === 'psu') {
        col1Header.textContent = 'Wattage / Efficiency';
        col2Header.textContent = 'Modularity / Standard';
      } else if (categoryId === 'case') {
        col1Header.textContent = 'Type / Form Factor';
        col2Header.textContent = 'Max GPU Clearance';
      } else if (categoryId === 'cooler') {
        col1Header.textContent = 'Type / Fan RPM';
        col2Header.textContent = 'Noise / Max TDP';
      } else {
        col1Header.textContent = 'Specification 1';
        col2Header.textContent = 'Specification 2';
      }
    }

    // Reset filters
    state.searchFilter = '';
    partSearchInput.value = '';
    state.selectedBrands.clear();

    populateBrandFilters();
    renderCatalogResults();

    partPickerModal.classList.add('active');
    lucide.createIcons();
  };

  function closeModal() {
    partPickerModal.classList.remove('active');
    state.activeCategory = null;
  }

  function populateBrandFilters() {
    const list = document.getElementById('manufacturerCheckboxList');
    list.innerHTML = '';
    const partsForCat = PARTS_DATABASE.filter(p => p.category === state.activeCategory);
    const brands = Array.from(new Set(partsForCat.map(p => p.brand.split('/')[0].trim())));

    brands.forEach(brand => {
      const label = document.createElement('label');
      label.className = 'checkbox-item';
      label.innerHTML = `
        <input type="checkbox" value="${escapeHtml(brand)}">
        <span>${escapeHtml(brand)}</span>
      `;
      const input = label.querySelector('input');
      input.checked = state.selectedBrands.has(brand);
      input.addEventListener('change', () => {
        if (input.checked) state.selectedBrands.add(brand);
        else state.selectedBrands.delete(brand);
        renderCatalogResults();
      });
      list.appendChild(label);
    });
  }

  function renderCatalogResults() {
    const tbody = document.getElementById('catalogTableBody');
    tbody.innerHTML = '';

    let parts = PARTS_DATABASE.filter(p => p.category === state.activeCategory);

    // Apply Condition filter and Price filter
    parts = parts.filter(p => {
      const newLoc = getLocalizedPartData(p, state.country, 'new');
      const usedLoc = getLocalizedPartData(p, state.country, 'used');

      if (state.modalCondition === 'new') {
        return newLoc.price <= state.maxPrice;
      } else if (state.modalCondition === 'used') {
        return usedLoc.price <= state.maxPrice;
      } else {
        return Math.min(newLoc.price, usedLoc.price) <= state.maxPrice;
      }
    });

    // Apply Brand filter
    if (state.selectedBrands.size > 0) {
      parts = parts.filter(p => {
        const partBrand = p.brand.split('/')[0].trim();
        return state.selectedBrands.has(partBrand);
      });
    }

    // Apply Search filter
    if (state.searchFilter) {
      parts = parts.filter(p =>
        p.name.toLowerCase().includes(state.searchFilter) ||
        p.brand.toLowerCase().includes(state.searchFilter)
      );
    }

    // Compatibility check for each item
    const itemsWithCompat = parts.map(part => {
      const isCompat = isPartCompatible(part);
      return { part, isCompat };
    });

    const visibleItems = state.hideIncompatible
      ? itemsWithCompat.filter(item => item.isCompat)
      : itemsWithCompat;

    const condLabel = state.modalCondition === 'all' ? 'All (New & Used)' : (state.modalCondition === 'used' ? 'Used Deals' : 'Brand New');
    document.getElementById('modalProductCount').textContent = `Showing ${visibleItems.length} parts [${condLabel}] in ${getCountryConfig(state.country).name}`;

    if (visibleItems.length === 0) {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td colspan="6" style="text-align: center; padding: 2.5rem; color: var(--text-muted);">
          No parts match your filter criteria in this price range. Try adjusting filters or condition.
        </td>
      `;
      tbody.appendChild(tr);
      return;
    }

    visibleItems.forEach(({ part, isCompat }) => {
      const tr = document.createElement('tr');
      if (!isCompat) tr.className = 'incompatible-row';

      const newLoc = getLocalizedPartData(part, state.country, 'new');
      const usedLoc = getLocalizedPartData(part, state.country, 'used');

      let priceCellHtml = '';
      let actionButtonsHtml = '';

      if (state.modalCondition === 'used') {
        priceCellHtml = `
          <div>
            <strong style="color: #fbbf24;">${formatCurrency(usedLoc.price)}</strong>
            <span class="used-savings-pill">Save ${usedLoc.savings_pct}%</span>
            <div style="font-size: 0.72rem; color: var(--text-dim); text-decoration: line-through;">New: ${formatCurrency(newLoc.price)}</div>
          </div>
        `;
        actionButtonsHtml = `
          <button class="btn btn-sm btn-primary" onclick="selectPartWithCondition('${part.id}', 'used')">
            <i data-lucide="tag"></i> Add Used
          </button>
        `;
      } else if (state.modalCondition === 'new') {
        priceCellHtml = `
          <div>
            <strong>${formatCurrency(newLoc.price)}</strong>
          </div>
        `;
        actionButtonsHtml = `
          <button class="btn btn-sm btn-primary" onclick="selectPartWithCondition('${part.id}', 'new')">
            <i data-lucide="plus"></i> Add New
          </button>
        `;
      } else {
        // All deals: show both prices and dual buttons
        priceCellHtml = `
          <div>
            <div><strong>${formatCurrency(newLoc.price)}</strong> <span style="font-size: 0.7rem; color: var(--text-muted);">New</span></div>
            <div style="margin-top: 2px;">
              <span style="color: #fbbf24; font-weight: 600;">${formatCurrency(usedLoc.price)}</span> 
              <span class="used-savings-pill">-${usedLoc.savings_pct}%</span>
            </div>
          </div>
        `;
        actionButtonsHtml = `
          <div style="display: flex; gap: 0.35rem; justify-content: flex-end;">
            <button class="btn btn-sm btn-outline" onclick="selectPartWithCondition('${part.id}', 'new')" title="Select as Brand New">
              New
            </button>
            <button class="btn btn-sm btn-primary" onclick="selectPartWithCondition('${part.id}', 'used')" title="Select as Pre-Owned (Save ${formatCurrency(usedLoc.savings)})">
              Used
            </button>
          </div>
        `;
      }

      tr.innerHTML = `
        <td>
          <div class="product-item">
            <div class="product-thumb"><i data-lucide="${CATEGORIES.find(c => c.id === part.category).icon}"></i></div>
            <div class="product-info">
              <span class="product-title">${escapeHtml(part.name)}</span>
              ${!isCompat ? '<span class="tag-incompat">Incompatible with current build</span>' : ''}
              <div class="product-submerchant">
                <i data-lucide="shopping-cart"></i> ${escapeHtml(newLoc.merchant)} | ♻️ ${escapeHtml(usedLoc.merchant)}
              </div>
            </div>
          </div>
        </td>
        <td><span class="spec-badge">${escapeHtml(part.specs.col1 || '-')}</span></td>
        <td><span class="spec-badge">${escapeHtml(part.specs.col2 || '-')}</span></td>
        <td>
          <div class="product-rating">
            <span class="stars-icon"><i data-lucide="star"></i></span>
            <strong>${part.rating}</strong>
            <span>(${part.reviews})</span>
          </div>
        </td>
        <td class="col-price">${priceCellHtml}</td>
        <td class="text-right">
          ${actionButtonsHtml}
        </td>
      `;
      tbody.appendChild(tr);
    });

    lucide.createIcons();
  }

  // =========================================================================
  // Part Mutation & Persistence
  // =========================================================================

  window.selectPart = function(partId) {
    selectPartWithCondition(partId, 'new');
  };

  window.selectPartWithCondition = function(partId, condition = 'new') {
    const part = PARTS_DATABASE.find(p => p.id === partId);
    if (!part) return;

    state.selectedParts[part.category] = part;
    state.partConditions[part.category] = condition;

    saveBuildState();
    closeModal();
    renderBuilderTable();
    updateDiagnosticsAndTotals();
    lucide.createIcons();

    const condLabel = condition === 'used' ? ' (Tested Pre-Owned)' : ' (Brand New)';
    showToast(`Added ${part.name}${condLabel}`, 'success');
  };

  window.removePart = function(categoryId) {
    const part = state.selectedParts[categoryId];
    delete state.selectedParts[categoryId];
    delete state.partConditions[categoryId];
    saveBuildState();
    renderBuilderTable();
    updateDiagnosticsAndTotals();
    lucide.createIcons();

    if (part) {
      showToast(`Removed ${part.name} from build`, 'info');
    }
  };

  window.loadPreset = function(presetKey) {
    applyPreset(presetKey);
  };

  function applyPreset(presetKey) {
    if (typeof PRESET_BUILDS === 'undefined') return;
    const preset = PRESET_BUILDS[presetKey];
    if (!preset) return;

    const isUsedPreset = (presetKey === 'used_budget');

    state.selectedParts = {};
    state.partConditions = {};

    Object.entries(preset.parts).forEach(([cat, partId]) => {
      const found = PARTS_DATABASE.find(p => p.id === partId);
      if (found) {
        state.selectedParts[cat] = found;
        state.partConditions[cat] = isUsedPreset ? 'used' : 'new';
      }
    });

    saveBuildState();
    renderBuilderTable();
    updateDiagnosticsAndTotals();
    lucide.createIcons();

    const presetNames = {
      used_budget: 'Used Value Champion (1080p)',
      budget: 'Budget Esports 1080p',
      midrange: 'Sweet Spot 1440p Gaming',
      enthusiast: '4K Ray-Tracing Monster'
    };
    showToast(`Loaded Build: ${presetNames[presetKey] || presetKey}`, 'success');

    const tableEl = document.getElementById('partsTable');
    if (tableEl) {
      tableEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function saveBuildState() {
    const mapped = {};
    Object.entries(state.selectedParts).forEach(([cat, p]) => {
      if (p) mapped[cat] = p.id;
    });
    localStorage.setItem('pickmypc_build', JSON.stringify(mapped));
    localStorage.setItem('pickmypc_conditions', JSON.stringify(state.partConditions));
  }

  // =========================================================================
  // Export & Share Logic
  // =========================================================================

  function updateExportText() {
    const parts = state.selectedParts;
    const cfg = getCountryConfig(state.country);

    let totalPrice = 0;
    let newTotal = 0;
    Object.entries(parts).forEach(([cat, p]) => {
      if (!p) return;
      const cond = state.partConditions[cat] || 'new';
      const loc = getLocalizedPartData(p, state.country, cond);
      const newLoc = getLocalizedPartData(p, state.country, 'new');
      totalPrice += loc.price;
      newTotal += newLoc.price;
    });

    const totalSavings = Math.max(0, newTotal - totalPrice);
    const formattedTotal = formatCurrency(totalPrice);
    const check = runCompatibilityCheck();

    if (currentExportTab === 'reddit') {
      let md = `[PCPartPicker Part List](${window.location.origin || 'https://pickmypc.local/'}) - ${cfg.flag} **${cfg.name}** (${cfg.currency})\n\n`;
      md += `Type|Item|Condition|Price (${cfg.currency})|Merchant\n`;
      md += `:----|:----|:----|:----|:----\n`;
      CATEGORIES.forEach(c => {
        const p = parts[c.id];
        if (p) {
          const cond = state.partConditions[c.id] || 'new';
          const loc = getLocalizedPartData(p, state.country, cond);
          const condLabel = cond === 'used' ? '**Used / Pre-Owned**' : 'New';
          md += `**${c.name}** | ${p.name} | ${condLabel} | ${formatCurrency(loc.price)} | ${loc.merchant}\n`;
        }
      });
      md += `| **Total** | | | **${formattedTotal}** | |\n`;
      if (totalSavings > 0) {
        md += `| **Total Savings with Used Deals** | | | **-${formatCurrency(totalSavings)}** | |\n`;
      }
      md += `| Estimated Wattage | ${check.totalWattage}W | | | |\n`;
      md += `| Generated by PickMyPC System Builder (${cfg.name} Market) |\n`;
      exportTextArea.value = md;
    } else if (currentExportTab === 'text') {
      let txt = `=================================================\n`;
      txt += `PickMyPC System Build Summary\n`;
      txt += `Region: ${cfg.flag} ${cfg.name} • Currency: ${cfg.currency} (${cfg.symbol})\n`;
      txt += `=================================================\n\n`;
      CATEGORIES.forEach(c => {
        const p = parts[c.id];
        if (p) {
          const cond = state.partConditions[c.id] || 'new';
          const loc = getLocalizedPartData(p, state.country, cond);
          const condLabel = cond === 'used' ? '[USED]' : '[NEW] ';
          txt += `${c.name.padEnd(16)}: ${condLabel} ${p.name.padEnd(34)} ${formatCurrency(loc.price)} @ ${loc.merchant}\n`;
        }
      });
      txt += `\n-------------------------------------------------\n`;
      txt += `TOTAL PRICE     : ${formattedTotal}\n`;
      if (totalSavings > 0) {
        txt += `USED SAVINGS    : -${formatCurrency(totalSavings)} saved vs new retail!\n`;
      }
      txt += `ESTIMATED POWER : ${check.totalWattage} Watts\n`;
      txt += `COMPATIBILITY   : ${check.compatible ? 'Verified (No conflicts)' : 'Issues Found'}\n`;
      txt += `=================================================\n`;
      exportTextArea.value = txt;
    } else if (currentExportTab === 'json') {
      const partsPayload = {};
      CATEGORIES.forEach(c => {
        const p = parts[c.id];
        if (p) {
          const cond = state.partConditions[c.id] || 'new';
          const loc = getLocalizedPartData(p, state.country, cond);
          partsPayload[c.id] = {
            id: p.id,
            name: p.name,
            brand: p.brand,
            category: p.category,
            condition: cond,
            price: loc.price,
            currency: loc.currency,
            merchant: loc.merchant,
            shipping: loc.shipping,
            savings: loc.savings,
            specs: p.specs
          };
        }
      });

      exportTextArea.value = JSON.stringify({
        generatedAt: new Date().toISOString(),
        region: {
          code: cfg.code,
          name: cfg.name,
          currency: cfg.currency,
          symbol: cfg.symbol
        },
        totalPrice,
        formattedTotalPrice: formattedTotal,
        totalSavings,
        formattedTotalSavings: formatCurrency(totalSavings),
        estimatedWattage: check.totalWattage,
        compatible: check.compatible,
        parts: partsPayload
      }, null, 2);
    }
  }

  function updateThemeIcon() {
    const icon = document.getElementById('themeIcon');
    const label = document.getElementById('themeToggleLabel');
    if (state.theme === 'theme-light') {
      if (icon) icon.setAttribute('data-lucide', 'moon');
      if (label) label.textContent = 'Dark Mode';
    } else {
      if (icon) icon.setAttribute('data-lucide', 'sun');
      if (label) label.textContent = 'White Mode';
    }
    lucide.createIcons();
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.toString()
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
});
