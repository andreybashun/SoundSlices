#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""act_evtol.py — кейс 1 мультифизики: eVTOL, цикл "масса <-> энергия".
Модель: импульсная теория (висение, FM), огибающая перехода, крейсер через
C_D0 + индуктивное сопротивление. Петля замыкания решается итерацией Клейни
до наименьшей неподвижной точки (= фронт Парето петли).
Sound-срез: derate_eff = s*delta_rel на все эффективности; L(s) — относительная
ошибка энергии миссии; теория: наклон A*sum(f)*delta_rel, A = 1/(1-K),
K = dE/dm * 1000/(e_pack*DoD) — петлевое усиление.
"""
import math

g=9.81; m_fix=730.0
n_rot=8; R=1.26; A_tot=n_rot*math.pi*R**2
rho0=1.225
FM=0.70; eta_el=0.85; eta_prop=0.80
V=55.0; Sw=6.0; CD0=0.03; AR=8.0; e_osw=0.85
e_pack=200.0; DoD=0.85          # Вт*ч/кг (пак), глубина разряда
t_h,t_t,t_c = 5/60, 2/60, 45/60 # висение / переход / крейсер, ч
delta_t=0.15                    # огибающая перехода (sound)

def powers(m_b, d=0.0):
    """Мощности режимов, кВт; d — derate эффективностей (s*delta_rel)."""
    W=(m_fix+m_b)*g
    P_h = W**1.5/math.sqrt(2*rho0*A_tot)/(FM*eta_el*(1-d))/1000
    P_ind_W = 2*W**2/(rho0*V*Sw*math.pi*e_osw*AR)
    P_par_W = 0.5*rho0*V**3*Sw*CD0
    P_c = (P_ind_W+P_par_W)/(eta_prop*(1-d))/1000
    P_t = (1+delta_t)*max(P_h,P_c)
    return P_h,P_t,P_c,P_ind_W

def E_mission(m_b,d=0.0):
    Ph,Pt,Pc,_=powers(m_b,d)
    return Ph*t_h+Pt*t_t+Pc*t_c

def klein(d=0.0,m_start=600.0,maxit=500,tol=1e-11):
    m=m_start
    for i in range(maxit):
        m2=E_mission(m,d)*1000/(e_pack*DoD)
        if abs(m2-m)<tol: return m2,i+1
        m=m2
    return m,maxit

if __name__=="__main__":
    m0,it0=klein(0.0)
    W0=(m0+m_fix)*g; Ph,Pt,Pc,P_ind_W=powers(m0); E0=E_mission(m0)
    f=[Ph*t_h/E0,Pt*t_t/E0,Pc*t_c/E0]
    dEdm=(1.5*Ph*1000/W0*g*t_h + 1.15*1.5*Ph*1000/W0*g*t_t
          + (2*P_ind_W/W0/eta_prop)*g*t_c)/1000
    K=dEdm*1000/(e_pack*DoD); A_loop=1/(1-K)
    print(f"m_b={m0:.1f} кг, MTOW={m0+m_fix:.0f} кг, E={E0:.1f} кВтч ({it0} итер.)")
    print(f"P: hover={Ph:.0f} trans={Pt:.0f} cruise={Pc:.0f} кВт; DL={W0/A_tot:.0f} Н/м2")
    print(f"петля: K={K:.3f}, A={A_loop:.3f}")
    delta_rel=0.10; eps=1e-4
    ms1,_=klein(eps*delta_rel)
    slope=((E_mission(ms1,eps*delta_rel)-E0)/E0)/eps
    print(f"наклон L(s) при s->0: {slope:.4f}; теория: {A_loop*delta_rel*sum(f):.4f}")
    for s in [0.05,0.1,0.2,0.3]:
        ms,_=klein(s*delta_rel)
        print(f"  s={s:.2f}  L(s)={(E_mission(ms,s*delta_rel)-E0)/E0:.4f}")
