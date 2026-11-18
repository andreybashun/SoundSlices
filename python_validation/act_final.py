# -*- coding: utf-8 -*-
"""
act_final.py — финальный вычислительный раунд спора о прикладной ТК.
Узел: батарея (Li-Po 150 Вт*ч/кг) -> ESC -> BLDC (Kv) -> винт (D), квадрокоптер.
Миссия: старт/набор (w=1.6, 15%), крейсер (w=0.5, 35%), висение (w=1.0, 50%).

Результат 1. 3-режимный sound-срез: огибающая КПД по каждому режиму
             eta_bar_r = min_d eta_eff_r(d); звуковая в пределах сетки.
Результат 2. Безразмерная метрика: L = int|M_slice - M_exact| dT / int M_exact dT
             (доля потерянной площади фронта) + нормированный Хаусдорф.
Результат 3. Линейность потерь по разбросу (Липшецу):
             L(s) ~ (phi/(1-1.5 phi)) * sum_r f_r * s*D_r/eta_typ_r,
             локальный наклон с поправкой (1 - s*K_mix)^-2.
Запуск: python3 act_final.py
"""
import numpy as np, math, json

# ---------------- модель ----------------
g=9.81; rho=1.225
V=14.8; Rb=0.06; Rm=0.05; eta_esc=0.93; P0=3.0
e_b=150*3600*0.8                       # Дж/кг полезной энергии
Ct,Cp=0.11,0.05
tip_max=160.0; I_max=25.0
av=5.0
PH=[('start',1.6,0.15),('cruise',0.5,0.35),('hover',1.0,0.50)]
m_fixed=0.45+4*(0.09+0.02+0.02)

D_list=np.round(np.linspace(0.20,0.36,7),4)
Kv_list=np.array([300,400,500,600,750],float)
T_list=np.round(np.arange(8,28.1,2.0),2)

def phase_calc(D,Kv_rad,Ttot):
    Tm=Ttot/4.0
    n=math.sqrt(Tm/(Ct*rho*D**4)); om=2*math.pi*n
    Pm=Cp*rho*n**3*D**5; tau=Pm/om
    Kt=1.0/Kv_rad; I=tau*Kt
    Veff=om/Kv_rad+I*(Rm+Rb)           # требуемое напряжение (дроссель <= 100%)
    A=math.pi*D**2                     # суммарная ометаемая площадь 4 дисков
    vi=math.sqrt(Ttot/(2*rho*A)); Pi=Ttot*vi
    ok=(om*D/2<=tip_max) and (I<=I_max) and (Veff<=V)
    return ok,Pi,(4*Pm+4*I*I*Rm+4*P0)/eta_esc+av

def evaluate(D,Kv,T_min):
    Kv_rad=Kv*2*math.pi/60; M=2.0
    for it in range(500):
        tot_E=0.0; etas=[]
        for name,w,ft in PH:
            ok,Pi,Pbat=phase_calc(D,Kv_rad,w*M*g)
            if not ok: return None
            etas.append(Pi/Pbat); tot_E+=ft*T_min*60*Pbat
        mb=tot_E/e_b; Mnew=m_fixed+mb
        if not math.isfinite(Mnew) or Mnew>50: return None
        if abs(Mnew-M)<1e-4: M=Mnew; break
        M=0.5*M+0.5*Mnew
    else: return None
    return (T_min,M,tuple(etas))

def slice_eval(D,T_min,eta_bar):
    M=2.0; A=math.pi*D**2
    for it in range(500):
        tot_E=0.0
        for name,w,ft in PH:
            Ttot=w*M*g
            if Ttot<=0: return None
            vi=math.sqrt(Ttot/(2*rho*A)); Pi=Ttot*vi
            tot_E+=ft*T_min*60*Pi/eta_bar[name]
        mb=tot_E/e_b; Mnew=m_fixed+mb
        if not math.isfinite(Mnew) or Mnew>50: return None
        if abs(Mnew-M)<1e-4: M=Mnew; break
        M=0.5*M+0.5*Mnew
    else: return None
    return M

# ---------------- данные и огибающие ----------------
records=[r for D in D_list for Kv in Kv_list for T in T_list
         if (r:=evaluate(D,Kv,T)) is not None]
by_phase={i:[] for i in range(3)}
for (T,M,et) in records:
    for i,e in enumerate(et): by_phase[i].append(e)
eta_min=[min(by_phase[i]) for i in range(3)]
eta_typ=[float(np.median(by_phase[i])) for i in range(3)]
eta_max=[max(by_phase[i]) for i in range(3)]

def front(eta_bar):
    fr=[]
    for T in T_list:
        ms=[slice_eval(D,T,eta_bar) for D in D_list]
        ms=[m for m in ms if m is not None]
        if ms: fr.append((T,min(ms)))
    return fr

f_glob  = front({n:eta_gmin for n in [p[0] for p in PH]}) if (eta_gmin:=min(eta_min)) else None
f_reg   = front({'start':eta_min[0],'cruise':eta_min[1],'hover':eta_min[2]})
f_naive = front({'start':eta_max[0],'cruise':eta_max[1],'hover':eta_max[2]})

# ---------------- метрики ----------------
Tr=(exact[0][0],exact[-1][0]) if (exact:=sorted(set((r[0],r[1]) for r in records))) else None
exact_front=[]; seen=set()
for T in T_list:
    ms=[r[1] for r in records if r[0]==T]
    if ms: exact_front.append((T,min(ms)))
exact=exact_front
Tr=(exact[0][0],exact[-1][0]); Mr=(exact[0][1],exact[-1][1])
def nHaus(fa,fb_):
    a=[((T-Tr[0])/(Tr[1]-Tr[0]),(M-Mr[0])/(Mr[1]-Mr[0])) for T,M in fa]
    b=[((T-Tr[0])/(Tr[1]-Tr[0]),(M-Mr[0])/(Mr[1]-Mr[0])) for T,M in fb_]
    one=lambda A,B: max(min(math.hypot(p[0]-q[0],p[1]-q[1]) for q in B) for p in A)
    return max(one(a,b),one(b,a))
def interp(f,T): return float(np.interp(T,[t for t,_ in f],[m for _,m in f]))
def area_ratio(fs,fe):
    Ts=[t for t,_ in fe]; Me_=[m for _,m in fe]; num=den=0.0
    for i in range(len(Ts)-1):
        m_e=Me_[i]; m_s=interp(fs,Ts[i])
        num+=abs(m_s-m_e)*(Ts[i+1]-Ts[i]); den+=m_e*(Ts[i+1]-Ts[i])
    return num/den if den>0 else float('nan')

print("метрики (L = отношение площадей, H = норм. Хаусдорф):")
for nm,f in [('global sound',f_glob),('regime sound',f_reg),('naive best-case',f_naive)]:
    print(f"  {nm:15s} L={area_ratio(f,exact):.4f}  H={nHaus(f,exact):.4f}")

# ---------------- линейность ----------------
deltas=[eta_typ[i]-eta_min[i] for i in range(3)]
phi=float(np.mean([(M-m_fixed)/M for T,M in exact]))
fb=1.0/(1.0-1.5*phi)
Kmix=fb and sum(PH[i][2]*deltas[i]/eta_typ[i] for i in range(3))
ss=np.arange(0,2.01,0.25); Ls=[]
for s in ss:
    eb={'start':eta_typ[0]-s*deltas[0],'cruise':eta_typ[1]-s*deltas[1],'hover':eta_typ[2]-s*deltas[2]}
    Ls.append(area_ratio(front(eb),exact))
Ls=np.array(Ls); mask=ss>=1.0
b,a=np.polyfit(ss[mask],Ls[mask],1)
r2=np.corrcoef(ss[mask],Ls[mask])[0,1]**2
slope_local=(fb*phi*Kmix)/(1-1.5*Kmix)**2
print(f"\nветвь s in [1,2]: наклон={b:.4f}, R2={r2:.4f}, теория={slope_local:.4f}")

if __name__=='__main__':
    json.dump({'exact':exact,'f_reg':f_reg,'f_glob':f_glob,'f_naive':f_naive,
               'ss':list(ss),'Ls':list(Ls),'slope':float(b),'r2':float(r2),
               'theory':float(slope_local)},open('final_protocol.json','w'))
    print('сохранено: final_protocol.json')
