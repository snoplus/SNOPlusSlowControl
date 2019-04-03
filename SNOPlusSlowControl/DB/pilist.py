#DeltaV channels and specifications
pi_list =[{"dbname":"UPW_plant_temp","channels":[1],"address":"DeltaV_311-TIT-146/AI1/PV.CV","method":1},\
              {"dbname":"cavity_water_level","channels":[1],"address":"DeltaV_311-PT087/SCLR1/OUT.CV","method":1},\
              {"dbname":"holddown_rope","channels":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],"address":"DeltaV_HDLC-AI-%02d/AI1/PV.CV","method":2},\
              {"dbname":"holdup_rope","channels":[1,2,3,4,5,6,7,8,9,10],"address":"DeltaV_AVLC-AI-%02d/AI1/PV.CV","method":2},\
              {"dbname":"equator_monitor","channels":[2,4,7,9],"address":"DeltaV_AVEQ-%02d/ALM1/PV.CV","method":2},\
              {"dbname":"cover_gas","channels":[1,2,3,4,5],"address":"DeltaV_UI_CG_%s/AI1/PV.CV","appendage":["UPPERBAG","MIDDLEBAG","LOWERBAG","O2","PT"],"method":3},\
              {"dbname":"AV_direction","channels":[1,2,3],"address":"DeltaV_AVDIR%d/ALM1/PV.CV","method":2},\
              {"dbname":"AV_height","channels":[1],"address":"DeltaV_AV-HEIGHT/ALM1/PV.CV","method":1},\
              {"dbname":"AV_buoyant_force","channels":[1],"address":"DeltaV_AV_CALCS/AV_BUOYANT_FORCE/PV.CV","method":1},\
              {"dbname":"AV_inner_weight","channels":[1],"address":"DeltaV_AV_CALCS/AV_INNER_WEIGHT/PV.CV","method":1},\
              {"dbname":"AV_total_force","channels":[1],"address":"DeltaV_AV_CALCS/AV_TOTAL_FORCE/PV.CV","method":1},\
              {"dbname":"creep","channels":[1],"address":"DeltaV_AV_CALCS/CREEP/PV.CV","method":1},\
              {"dbname":"hooke_law_psn","channels":[1],"address":"DeltaV_AV_CALCS/HOOKE_LAW_PSN/PV.CV","method":1},\
              {"dbname":"zerocreep_exp_dn","channels":[1],"address":"DeltaV_AV_CALCS/ZEROCREEP_EXP_DN/PV.CV","method":1},\
              {"dbname":"zerocreep_exp_up","channels":[1],"address":"DeltaV_AV_CALCS/ZEROCREEP_EXP_UP/PV.CV","method":1},\
              {"dbname":"down_torque_x","channels":[1],"address":"DeltaV_AV_CALCS_2/DOWN_TORQUE_X.CV","method":1},\
              {"dbname":"down_torque_y","channels":[1],"address":"DeltaV_AV_CALCS_2/DOWN_TORQUE_Y.CV","method":1},\
              {"dbname":"upward_torque_x","channels":[1],"address":"DeltaV_AV_CALCS_2/UPWARD_TORQUE_X.CV","method":1},\
              {"dbname":"upward_torque_y","channels":[1],"address":"DeltaV_AV_CALCS_2/UPWARD_TORQUE_Y.CV","method":1},\
              {"dbname":"cavity_bubbler","channels":[1],"address":"DeltaV_311-PT087/AI1/PV.CV","method":1},\
              {"dbname":"AV_inside_bubbler","channels":[1],"address":"DeltaV_321-PT410/AI1/PV.CV","method":1},\
              {"dbname":"AV_outside_bubbler","channels":[1],"address":"DeltaV_321-PT411/AI1/PV.CV","method":1},\
              {"dbname":"control_room_temp","channels":[1],"address":"BACnet_682100_SNO_AHU2_CTRL_RMT_TL Archive","method":1},\
              {"dbname":"deck_humidity","channels":[1],"address":"BACnet_682100_SNO_AHU2_DEC_RH_TL Archive","method":1},\
              {"dbname":"deck_temp","channels":[1],"address":"BACnet_682100_SNO_AHU2_DECK_RMT_TL Archive","method":1},\
              {"dbname":"AVsensorRope","channels":[1,2,3,4,5,6,7],"address":"DeltaV_SENSE_ROPE_%s/CALC1/OUT1.CV","appendage":["A","B","C","D","E","F","G"],"method":3},\
              {"dbname":"CavityRecircValveIsOpen","channels":[1,2,3,4,5,6,7],"address":"DeltaV_V-%s/DO1/PV_D.CV","appendage":["174","175","176","178-179","180","181",\
              "182"],"method":3},\
              {"dbname":"AVRecircValveIsOpen","channels":[1,2],"address":"DeltaV_V-%s/DO1/PV_D.CV","appendage":["754","755"],"method":3},\
              {"dbname":"AVneck","channels":[1,2,3,4,5,6],"address":"DeltaV_SENSE_CALCS/CALC1/OUT%s.CV","appendage":["1","2","3","4","5","6"],"method":3},\
              {"dbname":"P15IsRunning","channels":[1],"address":"DeltaV_311-P15/P15_RUNNING/PV_D.CV","method":1},\
              {"dbname":"P16IsRunning","channels":[1],"address":"DeltaV_311-P16/P16_ENABLE/PV_D.CV","method":1},\
              {"dbname":"UPS_output_load","channels":[1],"address":"SNMP_snoplusups01_upsOutputPercentLoad","method":1},\
              {"dbname":"UPS_time_on_battery","channels":[1],"address":"SNMP_snoplusups01_upsSecondsOnBattery","method":1},\
              {"dbname":"UPS_estimated_time_left","channels":[1],"address":"SNMP_snoplusups01_upsEstimatedMinutesRemaining","method":1},\
              {"dbname":"UPS_battery_status","channels":[1],"address":"SNMP_snoplusups01_upsBatteryStatus","method":1},\
              {"dbname":"UPS_input_voltage","channels":[1,2,3],"address":"SNMP_snoplusups01_upsInputVoltageLine%s.CV","appendage":["1","2","3"],"method":3},\
              {"dbname":"UPS_output_power","channels":[1,2,3],"address":"SNMP_snoplusups01_upsOutputPowerLine%s.CV","appendage":["1","2","3"],"method":3},\
              {"dbname":"UPS_output_voltage","channels":[1,2,3],"address":"SNMP_snoplusups01_upsOutputVoltageLine%s.CV","appendage":["1","2","3"],"method":3},\
              {"dbname":"AV_dP","channels":[1],"address":"DeltaV_321-DPT002/SCLR1/OUT.CV","method":1}]
#Any dbs not in this list will search for new data in the most recent minute according to now's time
#Any dbs in this list grab the most recent data point in the PI server
getrecent_list = ["deck_humidity","deck_temp","control_room_temp","cover_gas","equator_monitor","AVsensorRope","AVneck",\
        "CavityRecircValveIsOpen","AVRecircValveIsOpen","P15IsRunning",\
	"UPS_output_load","UPS_time_on_battery","UPS_estimated_time_left",\
	"UPS_battery_status","UPS_output_power","UPS_output_voltage",\
	"UPS_input_voltage","P16IsRunning"]

