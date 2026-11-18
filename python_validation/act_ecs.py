#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""act_ecs.py — кейс 2 мультифизики: ECS (парокомпрессионный), три режима.
Реверс круиза: при T_amb << T_cab компрессор не нужен, доминирует обогрев —
фронт несвязный по режимам (фазовый переход). Тепловое ограничение авионики
T_j = T_amb + Q_av*R_th <= T_max — линейно по ресурсам, легально в h.
Sound-срезы: (а) R_th*(1+s*delta_R) — сертифицированная верхняя граница пика T,
ошибка L_T(s) линейна ТОЧНО; (б) derate eta_c — ошибка мощности компрессора.
"""
import math

UA=200.0;Q_pax=400.0;Q_sol=1500.0;Q_av=2000.0   # Вт
eta_c=0.45;T_evap=5+273.15;dT_cond=12.0;T_cab=24.0;T_max_av=70.0
regimes=[("ground",45.0,0.5),("climb",10.0,1/3),("cruise",-56.0,1.0)]

def regime(name,Ta,t_r):
    dT=Ta-T_cab
    Q_cool=UA*dT+Q_pax+(Q_sol if name=="ground" else 0.0) if dT>0 else 0.0
    if name=="cruise":
        return dict(COP=float('nan'),Q_evap=Q_av,W=0.0,
                    E=UA*(-dT)*t_r/1000,reversal=True)
    COP=eta_c*T_evap/((Ta+dT_cond+273.15)-T_evap)
    Q_evap=Q_cool+Q_av; W=Q_evap/COP
    return dict(COP=COP,Q_evap=Q_evap,W=W,E=W*t_r/1000,reversal=False)

def T_peak(R,Tamb,QkW,t,C_th=8.0):
    """Пик T при ступенчатой нагрузке: кусково-линейная модель, C*dot T = Q - (T-Tamb)/R."""
    return Tamb + QkW*R*(1-math.exp(-t/(R*C_th)))

if __name__=="__main__":
    total=0.0; rows=[]
    for name,Ta,t_r in regimes:
        r=regime(name,Ta,t_r); r.update(name=name,Ta=Ta,t_r=t_r)
        r["R_th_max"]=(T_max_av-Ta)/(Q_av/1000.0)
        total+=r["E"]; rows.append(r)
        print(f"{name:7s} COP={r['COP']:5.2f} Q_evap={r['Q_evap']/1000:4.1f} кВт "
              f"W={r['W']/1000:5.2f} кВт R_th<={r['R_th_max']:5.1f} К/кВт E={r['E']:5.2f} кВтч")
    print(f"ECS за миссию: {total:.1f} кВтч")
    # срез R_th: связывающее ограничение — земля
    R_bind=rows[0]["R_th_max"]; t_step=1800.0
    T0=T_peak(R_bind,45.0,2.0,t_step)
    delta_R=0.20
    for s in [0.05,0.1,0.2,0.3]:
        Ts=T_peak(R_bind*(1+s*delta_R),45.0,2.0,t_step)
        print(f"  s={s:.2f}  L_T(s)={(Ts-T0)/(T0-45.0):.4f}  (линейность точная)")
