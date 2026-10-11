/**
 * PickMyPC - Real-World Gaming Benchmark & Performance Simulation Engine
 * Physically accurate FPS calculations based on real YouTube, TechPowerUp & Reddit hardware benchmarks.
 * Models: GPU rasterization, CPU draw-call limits, VRAM bandwidth thrashing, 1% Lows, and resolution scaling.
 */

(function () {
  'use strict';

  // 14 Curated Iconic Games Across Modern Graphics Engines, Sims & AAA Releases
  const BENCHMARK_GAMES = [
    {
      id: 'cs2',
      name: 'Counter-Strike 2',
      engine: 'Source 2 (DX11 / Vulkan)',
      genre: 'Competitive Esports',
      icon: 'crosshair',
      base1080: 245,
      base1440: 185,
      base4k: 110,
      cpuW: 0.52,
      gpuW: 0.48,
      vram: { p1080: 4, p1440: 6, p4k: 8 },
      fpsCap: null,
      notes: 'Scales heavily with CPU single-core IPC and 3D V-Cache; ideal for 240Hz+ monitors.'
    },
    {
      id: 'cp2077',
      name: 'Cyberpunk 2077: Phantom Liberty',
      engine: 'REDengine 4 (DirectX 12)',
      genre: 'Heavy AAA / Ray Tracing',
      icon: 'flame',
      base1080: 68,
      base1440: 44,
      base4k: 22,
      cpuW: 0.35,
      gpuW: 0.65,
      vram: { p1080: 8, p1440: 10, p4k: 12 },
      fpsCap: null,
      notes: 'Extremely demanding raster & RT workload; high GPU tier and 10GB+ VRAM recommended.'
    },
    {
      id: 'wukong',
      name: 'Black Myth: Wukong',
      engine: 'Unreal Engine 5.4 (Lumen & Nanite)',
      genre: 'Next-Gen Action RPG',
      icon: 'sparkles',
      base1080: 58,
      base1440: 38,
      base4k: 18,
      cpuW: 0.25,
      gpuW: 0.75,
      vram: { p1080: 8, p1440: 10, p4k: 16 },
      fpsCap: null,
      notes: 'Dense UE5 Nanite geometry and Lumen lighting severely punish GPUs under 8GB VRAM.'
    },
    {
      id: 'cod',
      name: 'Call of Duty: Warzone / BO6',
      engine: 'IW 9.0 (DirectX 12)',
      genre: 'Fast-Paced AAA Shooter',
      icon: 'target',
      base1080: 105,
      base1440: 74,
      base4k: 42,
      cpuW: 0.42,
      gpuW: 0.58,
      vram: { p1080: 6, p1440: 8, p4k: 10 },
      fpsCap: null,
      notes: 'Demands balanced high CPU & GPU power for smooth 120Hz+ framerates in battle royale.'
    },
    {
      id: 'gta5',
      name: 'Grand Theft Auto V / Online',
      engine: 'RAGE Engine (DirectX 11)',
      genre: 'Open World Mainstream',
      icon: 'car',
      base1080: 135,
      base1440: 102,
      base4k: 58,
      cpuW: 0.40,
      gpuW: 0.60,
      vram: { p1080: 4, p1440: 4, p4k: 6 },
      fpsCap: 187,
      notes: 'Broad hardware compatibility; runs buttery smooth at 100+ FPS on budget systems.'
    },
    {
      id: 'er',
      name: 'Elden Ring',
      engine: 'FromSoftware (DirectX 12)',
      genre: 'Action RPG / Open World',
      icon: 'shield',
      base1080: 60,
      base1440: 60,
      base4k: 46,
      cpuW: 0.30,
      gpuW: 0.70,
      vram: { p1080: 6, p1440: 8, p4k: 10 },
      fpsCap: 60,
      notes: 'Engine capped at 60 FPS by design; benchmark measures stability and 1% low drops.'
    },
    {
      id: 'bg3',
      name: "Baldur's Gate 3 (Act 3)",
      engine: 'Divinity 4.0 (DX11 / Vulkan)',
      genre: 'Deep RPG / Complex AI',
      icon: 'sword',
      base1080: 78,
      base1440: 58,
      base4k: 32,
      cpuW: 0.46,
      gpuW: 0.54,
      vram: { p1080: 8, p1440: 8, p4k: 12 },
      fpsCap: null,
      notes: 'Lower City crowds generate hundreds of draw-calls; heavy processor load.'
    },
    {
      id: 'fortnite',
      name: 'Fortnite (Chapter 5)',
      engine: 'Unreal Engine 5 (DX12)',
      genre: 'Esports Battle Royale',
      icon: 'zap',
      base1080: 120,
      base1440: 88,
      base4k: 48,
      cpuW: 0.45,
      gpuW: 0.55,
      vram: { p1080: 6, p1440: 8, p4k: 10 },
      fpsCap: null,
      notes: 'Highly scalable; easily hits 144Hz–240Hz on competitive settings.'
    },
    {
      id: 'arc_raiders',
      name: 'ARC Raiders',
      engine: 'Unreal Engine 5 (Nanite & Chaos Physics)',
      genre: 'Sci-Fi Extraction Shooter',
      icon: 'crosshair',
      base1080: 72,
      base1440: 48,
      base4k: 25,
      cpuW: 0.38,
      gpuW: 0.62,
      vram: { p1080: 8, p1440: 10, p4k: 14 },
      fpsCap: null,
      notes: 'High-intensity multiplayer extraction with massive machine destruction; demands strong GPU & 10GB+ VRAM.'
    },
    {
      id: 'beamng',
      name: 'BeamNG.drive (0.33+)',
      engine: 'Torque 3D (Real-Time Soft-Body Physics)',
      genre: 'Vehicle Physics Simulation',
      icon: 'truck',
      base1080: 95,
      base1440: 72,
      base4k: 42,
      cpuW: 0.58,
      gpuW: 0.42,
      vram: { p1080: 6, p1440: 8, p4k: 12 },
      fpsCap: null,
      notes: 'Deep real-time multithreaded soft-body physics; scales tremendously with fast high-core CPUs and RAM.'
    },
    {
      id: 'assetto_corsa',
      name: 'Assetto Corsa (CSP / Pure)',
      engine: 'Kunos Engine (DirectX 11 + Shaders)',
      genre: 'Sim Racing Champion',
      icon: 'gauge',
      base1080: 165,
      base1440: 125,
      base4k: 76,
      cpuW: 0.36,
      gpuW: 0.64,
      vram: { p1080: 6, p1440: 8, p4k: 12 },
      fpsCap: null,
      notes: 'Runs ultra fast in vanilla; Custom Shaders Patch (CSP) and traffic mods benefit from 8GB+ GPU VRAM.'
    },
    {
      id: 'rdr2',
      name: 'Red Dead Redemption 2',
      engine: 'RAGE Engine (Vulkan / DX12)',
      genre: 'Open-World AAA Masterpiece',
      icon: 'compass',
      base1080: 88,
      base1440: 62,
      base4k: 36,
      cpuW: 0.34,
      gpuW: 0.66,
      vram: { p1080: 6, p1440: 8, p4k: 12 },
      fpsCap: null,
      notes: 'Vast volumetric clouds, dense foliage, and water physics; runs exceptionally well on modern Vulkan.'
    },
    {
      id: 'alan_wake_2',
      name: 'Alan Wake 2',
      engine: 'Northlight (Mesh Shaders & Path Tracing)',
      genre: 'Heavy AAA / Next-Gen Tech',
      icon: 'eye',
      base1080: 52,
      base1440: 34,
      base4k: 16,
      cpuW: 0.28,
      gpuW: 0.72,
      vram: { p1080: 8, p1440: 12, p4k: 16 },
      fpsCap: null,
      notes: 'State-of-the-art mesh shaders and path tracing; GPUs with hardware mesh shader support strongly required.'
    },
    {
      id: 'fh5',
      name: 'Forza Horizon 5',
      engine: 'ForzaTech (DirectX 12)',
      genre: 'Open-World Racing AAA',
      icon: 'flag',
      base1080: 128,
      base1440: 98,
      base4k: 58,
      cpuW: 0.32,
      gpuW: 0.68,
      vram: { p1080: 6, p1440: 8, p4k: 12 },
      fpsCap: null,
      notes: 'One of the best-optimized PC titles; achieves 100+ FPS easily across 1440p and ultra graphical settings.'
    }
  ];

  // Benchmark State
  const perfState = {
    resolution: '1440p', // '1080p' | '1440p' | '4k'
    quality: 'ultra',    // 'low' | 'medium' | 'high' | 'ultra'
    upscale: 'native'    // 'native' | 'quality' | 'perf' | 'framegen'
  };

  /**
   * Hardware Scoring Engines
   */
  function getGpuSpecs(gpu) {
    if (!gpu) return { score: 12, vram: 2, name: 'Integrated Graphics' };
    const name = (gpu.specs && gpu.specs.chipset) ? gpu.specs.chipset : (gpu.name || '');

    // 4K Ultra Enthusiast
    if (/4090/i.test(name)) return { score: 230, vram: 24, name: 'RTX 4090' };
    if (/4080\s*super/i.test(name)) return { score: 175, vram: 16, name: 'RTX 4080 Super' };
    if (/4080/i.test(name)) return { score: 165, vram: 16, name: 'RTX 4080' };
    if (/7900\s*xtx/i.test(name)) return { score: 170, vram: 24, name: 'RX 7900 XTX' };
    if (/7900\s*xt/i.test(name)) return { score: 145, vram: 20, name: 'RX 7900 XT' };
    if (/7900\s*gre/i.test(name)) return { score: 130, vram: 16, name: 'RX 7900 GRE' };
    if (/4070\s*ti\s*super/i.test(name)) return { score: 148, vram: 16, name: 'RTX 4070 Ti Super' };
    if (/4070\s*ti/i.test(name)) return { score: 138, vram: 12, name: 'RTX 4070 Ti' };
    if (/4070\s*super/i.test(name)) return { score: 125, vram: 12, name: 'RTX 4070 Super' };
    if (/4070/i.test(name)) return { score: 110, vram: 12, name: 'RTX 4070' };
    if (/7800\s*xt/i.test(name)) return { score: 122, vram: 16, name: 'RX 7800 XT' };
    if (/7700\s*xt/i.test(name)) return { score: 105, vram: 12, name: 'RX 7700 XT' };
    if (/6950\s*xt/i.test(name)) return { score: 135, vram: 16, name: 'RX 6950 XT' };
    if (/6800\s*xt/i.test(name)) return { score: 118, vram: 16, name: 'RX 6800 XT' };
    if (/3090\s*ti/i.test(name)) return { score: 135, vram: 24, name: 'RTX 3090 Ti' };
    if (/3090/i.test(name)) return { score: 125, vram: 24, name: 'RTX 3090' };
    if (/3080\s*ti/i.test(name)) return { score: 122, vram: 12, name: 'RTX 3080 Ti' };
    if (/3080/i.test(name)) return { score: 115, vram: 10, name: 'RTX 3080' };

    // 1440p High-End & Mainstream
    if (/4060\s*ti\s*16/i.test(name)) return { score: 94, vram: 16, name: 'RTX 4060 Ti 16GB' };
    if (/4060\s*ti/i.test(name)) return { score: 92, vram: 8, name: 'RTX 4060 Ti' };
    if (/4060/i.test(name)) return { score: 72, vram: 8, name: 'RTX 4060' };
    if (/7600\s*xt/i.test(name)) return { score: 76, vram: 16, name: 'RX 7600 XT' };
    if (/7600/i.test(name)) return { score: 70, vram: 8, name: 'RX 7600' };
    if (/6750\s*xt/i.test(name)) return { score: 95, vram: 12, name: 'RX 6750 XT' };
    if (/6700\s*xt/i.test(name)) return { score: 90, vram: 12, name: 'RX 6700 XT' };
    if (/6600/i.test(name)) return { score: 62, vram: 8, name: 'RX 6600' };
    if (/3070\s*ti/i.test(name)) return { score: 98, vram: 8, name: 'RTX 3070 Ti' };
    if (/3070/i.test(name)) return { score: 92, vram: 8, name: 'RTX 3070' };
    if (/3060\s*ti/i.test(name)) return { score: 85, vram: 8, name: 'RTX 3060 Ti' };
    if (/3060/i.test(name)) return { score: 70, vram: 12, name: 'RTX 3060 12GB' };
    if (/2080\s*ti/i.test(name)) return { score: 95, vram: 11, name: 'RTX 2080 Ti' };
    if (/2080\s*super/i.test(name)) return { score: 85, vram: 8, name: 'RTX 2080 Super' };
    if (/2070\s*super/i.test(name)) return { score: 78, vram: 8, name: 'RTX 2070 Super' };
    if (/2060\s*super/i.test(name)) return { score: 68, vram: 8, name: 'RTX 2060 Super' };
    if (/5700\s*xt/i.test(name)) return { score: 68, vram: 8, name: 'RX 5700 XT' };
    if (/a770/i.test(name)) return { score: 72, vram: 16, name: 'Intel Arc A770' };
    if (/a750/i.test(name)) return { score: 65, vram: 8, name: 'Intel Arc A750' };
    if (/a580/i.test(name)) return { score: 55, vram: 8, name: 'Intel Arc A580' };

    // Budget 1080p & Secondary Market
    if (/3050/i.test(name)) return { score: 48, vram: 8, name: 'RTX 3050' };
    if (/1660\s*super/i.test(name)) return { score: 42, vram: 6, name: 'GTX 1660 Super' };
    if (/1660/i.test(name)) return { score: 38, vram: 6, name: 'GTX 1660' };
    if (/1650/i.test(name)) return { score: 28, vram: 4, name: 'GTX 1650' };
    if (/1080\s*ti/i.test(name)) return { score: 78, vram: 11, name: 'GTX 1080 Ti' };
    if (/1080/i.test(name)) return { score: 65, vram: 8, name: 'GTX 1080' };
    if (/1070/i.test(name)) return { score: 52, vram: 8, name: 'GTX 1070' };
    if (/1060/i.test(name)) return { score: 40, vram: 6, name: 'GTX 1060 6GB' };
    if (/580/i.test(name)) return { score: 34, vram: 8, name: 'RX 580 8GB' };
    if (/980\s*ti/i.test(name)) return { score: 45, vram: 6, name: 'GTX 980 Ti' };
    if (/970/i.test(name)) return { score: 32, vram: 4, name: 'GTX 970' };
    if (/750\s*ti/i.test(name)) return { score: 16, vram: 2, name: 'GTX 750 Ti' };
    if (/r9\s*fury/i.test(name)) return { score: 40, vram: 4, name: 'R9 Fury X' };
    if (/r9\s*290/i.test(name)) return { score: 30, vram: 4, name: 'R9 290X' };
    if (/7970/i.test(name)) return { score: 22, vram: 3, name: 'HD 7970' };

    return { score: 20, vram: 2, name: name };
  }

  function getCpuSpecs(cpu) {
    if (!cpu) return { score: 25, cores: 4, name: 'Basic CPU' };
    const name = cpu.name || '';

    // Ultimate Gaming
    if (/7800x3d|9800x3d/i.test(name)) return { score: 142, cores: 8, name: 'Ryzen 7 7800X3D' };
    if (/7950x3d|7900x3d/i.test(name)) return { score: 140, cores: 16, name: 'Ryzen 9 7950X3D' };
    if (/14900k|13900k/i.test(name)) return { score: 136, cores: 24, name: 'Core i9-14900K' };
    if (/9950x|7950x/i.test(name)) return { score: 135, cores: 16, name: 'Ryzen 9 9950X' };
    if (/14700k|13700k/i.test(name)) return { score: 125, cores: 20, name: 'Core i7-14700K' };
    if (/9900x|7900x/i.test(name)) return { score: 125, cores: 12, name: 'Ryzen 9 9900X' };
    if (/5800x3d|5700x3d/i.test(name)) return { score: 115, cores: 8, name: 'Ryzen 7 5800X3D' };
    if (/9700x|7700x|7700/i.test(name)) return { score: 110, cores: 8, name: 'Ryzen 7 7700X' };

    // Sweet Spot Mainstream
    if (/14600k|13600k/i.test(name)) return { score: 105, cores: 14, name: 'Core i5-14600K' };
    if (/9600x|7600x/i.test(name)) return { score: 100, cores: 6, name: 'Ryzen 5 7600X' };
    if (/7600|7500f/i.test(name)) return { score: 92, cores: 6, name: 'Ryzen 5 7600' };
    if (/12700k|12600k/i.test(name)) return { score: 88, cores: 10, name: 'Core i5-12600K' };
    if (/5900x|5950x/i.test(name)) return { score: 86, cores: 12, name: 'Ryzen 9 5900X' };
    if (/5700x|5800x/i.test(name)) return { score: 80, cores: 8, name: 'Ryzen 7 5700X' };
    if (/5600x|5600/i.test(name)) return { score: 75, cores: 6, name: 'Ryzen 5 5600' };
    if (/14400|13400|12400/i.test(name)) return { score: 74, cores: 6, name: 'Core i5-13400' };

    // Budget & Older Generations
    if (/10600k|11600k/i.test(name)) return { score: 65, cores: 6, name: 'Core i5-10600K' };
    if (/3700x|3800x/i.test(name)) return { score: 62, cores: 8, name: 'Ryzen 7 3700X' };
    if (/3600x|3600/i.test(name)) return { score: 55, cores: 6, name: 'Ryzen 5 3600' };
    if (/10400|11400/i.test(name)) return { score: 58, cores: 6, name: 'Core i5-10400' };
    if (/2600|2700/i.test(name)) return { score: 42, cores: 6, name: 'Ryzen 5 2600' };
    if (/1600/i.test(name)) return { score: 35, cores: 6, name: 'Ryzen 5 1600' };

    return { score: 50, cores: 6, name: name };
  }

  function getRamGb(memory) {
    if (!memory) return 16;
    const name = (memory.name || '') + ' ' + (memory.specs && memory.specs.col1 ? memory.specs.col1 : '');
    const match = name.match(/(\d+)\s*GB/i);
    return match ? parseInt(match[1], 10) : 16;
  }

  /**
   * Physics-accurate FPS calculation for a single game
   */
  function calculateGameFps(game, cpuScore, gpuScore, vramGb, ramGb, res, quality, upscale, gpuName) {
    const REF_GPU = 70; // Reference baseline: RTX 3060 12GB
    const REF_CPU = 75; // Reference baseline: Ryzen 5 5600

    const gpuRatio = Math.max(0.08, gpuScore / REF_GPU);
    const cpuRatio = Math.max(0.12, cpuScore / REF_CPU);

    const baseFps = res === '1080p' ? game.base1080 : (res === '1440p' ? game.base1440 : game.base4k);

    // Realistic In-Game Graphics Settings Scaling: Low, Medium, High, Ultra
    let qualMult = 1.0;
    if (quality === 'low') {
      qualMult = 1.55; // Low / Competitive settings: minimal shadows & post-processing
    } else if (quality === 'medium') {
      qualMult = 1.28; // Medium settings: standard textures and effects
    } else if (quality === 'high') {
      qualMult = 1.10; // High settings: rich details and high AF
    } else if (quality === 'ultra') {
      qualMult = 1.00; // Ultra settings: max volumetric, max draw distance, RT
    } else if (quality === 'competitive') {
      qualMult = 1.45;
    }

    const gpuPow = res === '1080p' ? 0.88 : (res === '1440p' ? 0.95 : 1.02);
    const gpuScale = Math.pow(gpuRatio, gpuPow);
    const cpuScale = Math.pow(cpuRatio, 0.85);

    let fpsGpu = baseFps * gpuScale * qualMult;
    let fpsCpuCeil = (baseFps / game.cpuW) * cpuScale * qualMult;

    // Detect GPU architecture capabilities for DLSS / FSR / Frame Gen
    const isNvidia = /rtx|gtx/i.test(gpuName || '');
    const isRtx40 = /40\d\d/i.test(gpuName || '');
    const isRtx = /rtx\s*(20|30|40)/i.test(gpuName || '');
    const isRadeonModern = /rx\s*(6|7)\d\d\d/i.test(gpuName || '');

    let upscaleTech = 'FSR';
    let upscaleLabel = '';

    // Apply Upscaling (Super Resolution) multipliers to GPU rasterization workload
    if (upscale === 'quality') {
      // Quality render: 1.40x to 1.45x GPU rendering boost
      const boost = (res === '4k') ? 1.46 : ((res === '1440p') ? 1.36 : 1.25);
      fpsGpu *= boost;
      upscaleTech = isRtx ? 'DLSS 3.5' : (isRadeonModern ? 'FSR 3' : 'FSR 2');
      upscaleLabel = `${upscaleTech} Quality`;
    } else if (upscale === 'perf') {
      // Performance render: 1.75x to 1.95x GPU rendering boost
      const boost = (res === '4k') ? 1.95 : ((res === '1440p') ? 1.68 : 1.45);
      fpsGpu *= boost;
      upscaleTech = isRtx ? 'DLSS 3.5' : (isRadeonModern ? 'FSR 3' : 'FSR 2');
      upscaleLabel = `${upscaleTech} Performance`;
    }

    // Harmonic pipeline formula (computes real bottlenecked FPS before frame generation)
    let rawFps = 1 / ((game.gpuW / fpsGpu) + (game.cpuW / fpsCpuCeil));

    // Frame Generation (Hardware Optical Flow Acceleration or FSR 3 Fluid Motion Frames)
    let frameGenActive = false;
    if (upscale === 'framegen') {
      // Quality upscale + Optical Multi-Frame Generation
      const baseUpscaleBoost = (res === '4k') ? 1.42 : ((res === '1440p') ? 1.32 : 1.22);
      const preFgGpu = fpsGpu * baseUpscaleBoost;
      const preFgFps = 1 / ((game.gpuW / preFgGpu) + (game.cpuW / fpsCpuCeil));

      // Frame generation adds synthesized frames (~1.72x to 1.88x display FPS)
      const fgFactor = isRtx40 ? 1.85 : 1.70;
      rawFps = preFgFps * fgFactor;
      frameGenActive = true;

      upscaleTech = isRtx40 ? 'DLSS 3 (Frame Gen)' : (isRadeonModern ? 'AFMF / FSR 3 (Frame Gen)' : 'FSR 3 Frame Gen');
      upscaleLabel = upscaleTech;
    }

    // VRAM deficit penalty
    const vramReq = res === '1080p' ? game.vram.p1080 : (res === '1440p' ? game.vram.p1440 : game.vram.p4k);
    let vramPenalty = false;
    if (vramGb < vramReq) {
      const diff = vramReq - vramGb;
      if (diff >= 4) {
        rawFps *= 0.62;
        vramPenalty = true;
      } else if (diff >= 2) {
        rawFps *= 0.82;
        vramPenalty = true;
      } else {
        rawFps *= 0.92;
      }
    }

    // RAM capacity penalty
    if (ramGb < 8) {
      rawFps *= 0.70;
    } else if (ramGb < 16 && (vramReq >= 8 || res === '4k')) {
      rawFps *= 0.88;
    }

    // Hard engine caps (Frame generation can bypass standard game lock in display mode)
    let isCapped = false;
    if (game.fpsCap && !frameGenActive && rawFps >= game.fpsCap) {
      rawFps = game.fpsCap;
      isCapped = true;
    }

    const avg = Math.max(1, Math.round(rawFps));
    let stabilityFactor = 0.78;
    if (ramGb >= 32) stabilityFactor += 0.04;
    if (vramPenalty) stabilityFactor -= 0.12;
    if (frameGenActive) stabilityFactor -= 0.08; // Frame gen has slightly higher frame-time variance

    const low1 = Math.max(1, Math.round(avg * stabilityFactor));

    return {
      avg,
      low1,
      isCapped,
      vramPenalty,
      upscaleTech,
      upscaleLabel,
      frameGenActive
    };
  }

  /**
   * Determine Overall Gaming Tier & Bottleneck Health
   */
  function evaluateSystem(cpuScore, gpuScore, res, avgFps) {
    // Gaming Tier
    let tier = {
      badge: 'Tier B',
      title: '1080p Ultra / 1440p Smooth',
      icon: 'sparkles',
      class: 'tier-b',
      desc: 'Smooth 60–100+ FPS in modern titles at high graphical presets.'
    };

    if (gpuScore >= 160 && avgFps >= 65 && res === '4k') {
      tier = {
        badge: 'Tier S',
        title: '4K Ultra & Ray-Tracing Beast',
        icon: 'crown',
        class: 'tier-s',
        desc: 'Crushes 4K 60–120+ FPS with maximum ray tracing, path tracing, and high graphics.'
      };
    } else if (gpuScore >= 110 && (avgFps >= 80 || res === '1440p')) {
      tier = {
        badge: 'Tier A',
        title: '1440p High Refresh Rate Champion',
        icon: 'award',
        class: 'tier-a',
        desc: 'Uncompromising 100–165+ FPS performance at 2K QHD for high-refresh competitive displays.'
      };
    } else if (gpuScore < 45 || avgFps < 50) {
      tier = {
        badge: 'Tier C',
        title: '1080p Esports & Budget Value',
        icon: 'zap',
        class: 'tier-c',
        desc: 'Solid 60–144+ FPS in esports titles (CS2, Valorant, GTA V); medium settings in heavy AAA games.'
      };
    }

    // Bottleneck Balance
    const idealRatio = res === '1080p' ? 0.90 : (res === '1440p' ? 0.70 : 0.50);
    const actualRatio = cpuScore / gpuScore;
    let bottleneckInfo = {
      pct: '98%',
      status: 'Optimal Balance',
      type: 'gpu-bound',
      summary: 'GPU-Bound (Ideal for Gaming): Graphics card is utilized to its maximum potential.'
    };

    if (actualRatio < (idealRatio * 0.72)) {
      const drop = Math.min(35, Math.round((1 - (actualRatio / idealRatio)) * 100));
      bottleneckInfo = {
        pct: `${drop}% CPU Limit`,
        status: 'CPU Bottleneck Notice',
        type: 'cpu-bound',
        summary: `At ${res.toUpperCase()}, the CPU may hold back the GPU's maximum framerate in esports or crowded scenes.`
      };
    } else if (actualRatio > (idealRatio * 1.7)) {
      bottleneckInfo = {
        pct: 'GPU Headroom',
        status: 'Ample CPU Headroom',
        type: 'gpu-bound',
        summary: 'Excellent processor headroom; can easily support a more powerful graphics card in future upgrades.'
      };
    }

    return { tier, bottleneckInfo };
  }

  /**
   * Main Render Function
   */
  function updateGamingBenchmarks() {
    const section = document.getElementById('gamingPerformanceSection');
    if (!section) return;

    // Get selected parts from window or builder state
    let parts = {};
    if (typeof window.getSelectedParts === 'function') {
      parts = window.getSelectedParts();
    } else if (window.__currentBuildParts) {
      parts = window.__currentBuildParts;
    }

    const cpu = parts.cpu || null;
    const gpu = parts.gpu || null;
    const memory = parts.memory || null;

    const noPartsCard = document.getElementById('perfEmptyState');
    const perfActiveView = document.getElementById('perfActiveView');

    if (!cpu && !gpu) {
      if (noPartsCard) noPartsCard.style.display = 'block';
      if (perfActiveView) perfActiveView.style.display = 'none';
      const statusPill = document.getElementById('statusFpsValue');
      if (statusPill) statusPill.textContent = 'Add CPU & GPU';
      return;
    }

    if (noPartsCard) noPartsCard.style.display = 'none';
    if (perfActiveView) perfActiveView.style.display = 'block';

    const cpuData = getCpuSpecs(cpu);
    const gpuData = getGpuSpecs(gpu);
    const ramGb = getRamGb(memory);

    // Calculate all game FPS for current resolution, quality, and upscale/frame gen setting
    const gameResults = BENCHMARK_GAMES.map(game => {
      const res = calculateGameFps(
        game,
        cpuData.score,
        gpuData.score,
        gpuData.vram,
        ramGb,
        perfState.resolution,
        perfState.quality,
        perfState.upscale,
        gpuData.name
      );
      return { game, ...res };
    });

    // Average FPS across non-capped titles or overall
    const sumFps = gameResults.reduce((acc, g) => acc + g.avg, 0);
    const avgFps = Math.round(sumFps / gameResults.length);

    const sumLow = gameResults.reduce((acc, g) => acc + g.low1, 0);
    const avgLow = Math.round(sumLow / gameResults.length);

    const { tier, bottleneckInfo } = evaluateSystem(cpuData.score, gpuData.score, perfState.resolution, avgFps);

    // Update Top Summary KPI Badges
    const tierBadge = document.getElementById('perfTierBadge');
    const tierTitle = document.getElementById('perfTierTitle');
    const tierDesc = document.getElementById('perfTierDesc');
    if (tierBadge) {
      tierBadge.className = `tier-pill ${tier.class}`;
      tierBadge.textContent = tier.badge;
    }
    if (tierTitle) tierTitle.textContent = tier.title;
    if (tierDesc) tierDesc.textContent = tier.desc;

    const kpiAvgEl = document.getElementById('perfKpiAvgFps');
    const kpiLowEl = document.getElementById('perfKpiLowFps');
    const kpiBottleEl = document.getElementById('perfKpiBottleneck');
    const kpiBottleDesc = document.getElementById('perfKpiBottleDesc');

    if (kpiAvgEl) kpiAvgEl.textContent = `${avgFps} FPS`;
    if (kpiLowEl) kpiLowEl.textContent = `${avgLow} FPS`;
    if (kpiBottleEl) kpiBottleEl.textContent = bottleneckInfo.status;
    if (kpiBottleDesc) kpiBottleDesc.textContent = bottleneckInfo.summary;

    // Update Header Status Bar Card
    const statusPill = document.getElementById('statusFpsValue');
    if (statusPill) {
      const fgTag = (perfState.upscale === 'framegen') ? ' + Frame Gen' : (perfState.upscale !== 'native' ? ' + Upscaling' : '');
      statusPill.textContent = `~${avgFps} FPS (${perfState.resolution.toUpperCase()}${fgTag})`;
    }

    // Render Game Cards Grid
    const grid = document.getElementById('perfGameCardsGrid');
    if (grid) {
      grid.innerHTML = '';

      gameResults.forEach(item => {
        const { game, avg, low1, isCapped, vramPenalty, upscaleLabel, frameGenActive } = item;

        let statusClass = 'fps-ultra';
        let statusText = '144Hz+ Ready';
        if (avg < 35) {
          statusClass = 'fps-low';
          statusText = 'Demanding';
        } else if (avg < 60) {
          statusClass = 'fps-playable';
          statusText = 'Playable';
        } else if (avg < 120) {
          statusClass = 'fps-smooth';
          statusText = 'Smooth (60+ FPS)';
        }

        const barPct = Math.min(100, Math.round((avg / 240) * 100));

        let pillHtml = '';
        if (perfState.upscale !== 'native' && upscaleLabel) {
          const pillClass = upscaleLabel.includes('DLSS') ? 'dlss' : 'fsr';
          const iconName = frameGenActive ? 'sparkles' : 'cpu';
          pillHtml = `<div class="card-upscale-pill ${pillClass}"><i data-lucide="${iconName}"></i> ${escapeHtml(upscaleLabel)}</div>`;
        }

        const card = document.createElement('div');
        card.className = 'game-perf-card';
        card.innerHTML = `
          <div class="card-game-header">
            <div>
              <span class="game-genre-tag">${escapeHtml(game.genre)}</span>
              <h4 class="game-name">${escapeHtml(game.name)}</h4>
              <span class="game-engine-label">${escapeHtml(game.engine)}</span>
              ${pillHtml}
            </div>
            <div class="game-fps-badge ${statusClass}">
              <span class="fps-num">${avg}</span>
              <span class="fps-unit">FPS</span>
            </div>
          </div>

          <div class="card-fps-meter">
            <div class="meter-bar-track">
              <div class="meter-bar-fill ${statusClass}" style="width: ${barPct}%;"></div>
              <div class="marker marker-60" title="60 FPS Console Standard"></div>
              <div class="marker marker-144" title="144 FPS High Refresh Standard"></div>
            </div>
            <div class="meter-labels">
              <span>0 FPS</span>
              <span class="label-60">60 FPS</span>
              <span class="label-144">144 FPS</span>
              <span>240+</span>
            </div>
          </div>

          <div class="card-details-row">
            <div class="detail-item">
              <span class="detail-label">1% Low:</span>
              <span class="detail-val">${low1} FPS</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Experience:</span>
              <span class="detail-status ${statusClass}">${statusText}</span>
            </div>
          </div>

          <div class="card-game-note">
            <i data-lucide="info"></i>
            <span>${isCapped ? '🔒 Hard-capped at 60 FPS in engine. ' : ''}${vramPenalty ? '⚠️ High VRAM usage at this resolution. ' : ''}${escapeHtml(game.notes)}</span>
          </div>
        `;
        grid.appendChild(card);
      });
    }

    if (window.lucide) {
      window.lucide.createIcons();
    }
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

  // Initialize UI controls
  function initControls() {
    // Resolution Toggles
    const resWrap = document.getElementById('perfResToggles');
    if (resWrap) {
      resWrap.querySelectorAll('.perf-toggle-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          resWrap.querySelectorAll('.perf-toggle-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          perfState.resolution = btn.dataset.res;
          updateGamingBenchmarks();
        });
      });
    }

    // Quality Toggles
    const qualityWrap = document.getElementById('perfPresetToggles');
    if (qualityWrap) {
      qualityWrap.querySelectorAll('.perf-toggle-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          qualityWrap.querySelectorAll('.perf-toggle-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          perfState.quality = btn.dataset.quality;
          updateGamingBenchmarks();
        });
      });
    }

    // Upscale & Frame Gen Toggles
    const upscaleWrap = document.getElementById('perfUpscaleToggles');
    if (upscaleWrap) {
      upscaleWrap.querySelectorAll('.perf-toggle-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          upscaleWrap.querySelectorAll('.perf-toggle-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          perfState.upscale = btn.dataset.upscale;
          updateGamingBenchmarks();
        });
      });
    }
  }

  // Public Engine API
  window.GamingBenchmarkEngine = {
    update: updateGamingBenchmarks,
    init: initControls,
    setResolution: (res) => { perfState.resolution = res; updateGamingBenchmarks(); },
    setQuality: (q) => { perfState.quality = q; updateGamingBenchmarks(); },
    setUpscale: (u) => { perfState.upscale = u; updateGamingBenchmarks(); },
    getState: () => ({ ...perfState })
  };

  // Wire up when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      initControls();
      updateGamingBenchmarks();
    });
  } else {
    initControls();
    updateGamingBenchmarks();
  }
})();
