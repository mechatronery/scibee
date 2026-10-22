include <Hardwvare.scad>
include <Structure.scad>
include <Pump_adapter.scad>


/* [Parameters] */


/* [3D printer capabilities] */
// 3D printer tolerance
tol=0.1;    // 0.01
// 3D printer extrusion width
layW=0.45;  // 0.01
// 3D printer first layer hight
layH1=0.2;   // 0.01
// 3D printer layer hight
layH=0.2;   // 0.01


/* [Hidden] */
$fn= $preview ? 30 : 180;
INtoMM=25.4;


ofst=3+2;
baseTH=3;


if($preview)
{
    // frame
    if(true) translate([-430/2+100*3,-202/2+100,0]) color([196/255,164/255,132/255])
    {
        translate([0,202/2+10/2,25/2-ofst]) cube([430+10*2,10,25], center=true);
            translate([430/2+10/2,0,25/2-ofst]) cube([10,202,35], center=true);
            translate([-430/2-10/2,0,25/2-ofst]) cube([10,202,35], center=true);
        translate([0,-202/2-10/2,25/2-ofst]) cube([430+10*2,10,20], center=true);
    }
    
    // mounting plate
    color([0.2,0.2,0.2])
    {
        translate([-100,0,0]) MountingPlate_RPi_edge();
        translate([0,0,0]) MountingPlate_RPi();
        translate([100,0,0]) MountingPlate();
        translate([2*100,0,0]) MountingPlate(true);
            translate([3*100,0,0]) MountingPlate_edge();
    }
    
    // USB socket holder
    translate([0,-102,25/2-ofst]) rotate([0,-90,0]) color([0.2,0.2,0.2])
    {
        USB_holder();
        translate([0,0,-50]) USB_UARTadapter_holder();
    }
    
    // boards
    if(true)
    {
        // SCIBee
        union()
        {
            translate([0,0,0]) SCIBee_controllboard();
            translate([100,0,0]) SCIBee_controllboard();
            translate([200,0,0]) SCIBee_controllboard();
        }
            // Power meter
            translate([200+70,-20,0])
            {
                color([0.2,0.2,0.2]) difference()
                {
                    hull()
                    {
                        translate([0,(0.8*INtoMM)/2,0]) cylinder(r=0.1*INtoMM, h=1.55);
                        translate([0,-(0.8*INtoMM)/2,0]) cylinder(r=0.1*INtoMM, h=1.55);
                        translate([-0.6*INtoMM,(0.8*INtoMM)/2,0]) cylinder(r=0.1*INtoMM, h=1.55);
                        translate([-0.6*INtoMM,-(0.8*INtoMM)/2,0]) cylinder(r=0.1*INtoMM, h=1.55);
                    }
                    
                    translate([0,(0.8*INtoMM)/2,-0.1/2]) cylinder(d=0.1*INtoMM, h=1.7);
                    translate([0,-(0.8*INtoMM)/2,-0.1/2]) cylinder(d=0.1*INtoMM, h=1.7);
                }
                color([0.1,0.8,0.1])
                {
                    translate([-6.9/2+0.1*INtoMM,0,8.4/2+1.6]) cube([6.9,10.9,8.4], center=true);
                }
                color([0.9,0.9,0.8])
                {
                    translate([-9,-4.4/2+(1*INtoMM)/2,3.1/2+1.6]) cube([6.3,4.4,3.1], center=true);
                    translate([-9,4.4/2-(1*INtoMM)/2,3.1/2+1.6]) cube([6.3,4.4,3.1], center=true);
                }
            }
            
            // DCDC
            if(true) translate([-2,-15,1.6/2-ofst+0.5])
            {
                color([0.2,0.2,0.2]) cube([43.5,20.4,1.57], center=true);
                color([0.7,0.7,0.7])
                {
                    translate([43.5/2-3,15/2,0]) cube([3.3,3.3,1.6], center=true);
                    translate([43.5/2-3,-15/2,0]) cube([3.3,3.3,1.6], center=true);
                    translate([43.5/2-3-25,15/2,0]) cube([3.3,3.3,1.6], center=true);
                    translate([43.5/2-3-25,-15/2,0]) cube([3.3,3.3,1.6], center=true);
                }
            }
        // RPi
        color([0.7,0.8,0.6])
        {
            translate([-42-49,72.5,2+20]) rotate([0,0,-90]) translate([58/2+3.5,24.55-23/2,2]) import("raspberry pi zero 2 w.stl");
            translate([-40,30,0]) rotate([90,0,-90]) import("RASPBERRY_PI_5_WITH_ACTIVE_COOLER.stl");
        }
    }
}
else
{
    
}


// ===== ===== Structures ===== =====
module SCIBee_controllboard()
{
    color([0.1,0.8,0.1]) import("SCIBee_v1.11B.stl");
    translate([73,73,1.55])
    {
        //translate([0,0,2.1]) rotate([0,0,-90]) MZB3004T04();
        //translate([0,0,2+4.1+28.3/2+8]) rotate([0,90,-360/12*4]) Tjoint();
        
        translate([MHspc/2,MHspc/2,25-10]) rotate([180,0,0]) Bolt("M3",25,"Flat","HEX",2.5);
        translate([MHspc/2,-MHspc/2,25-10]) rotate([180,0,0]) Bolt("M3",25,"Flat","HEX",2.5);
        translate([-MHspc/2,MHspc/2,25-10]) rotate([180,0,0]) Bolt("M3",25,"Flat","HEX",2.5);
        translate([-MHspc/2,-MHspc/2,25-10]) rotate([180,0,0]) Bolt("M3",25,"Flat","HEX",2.5);
        translate([MHspc/3,0,15-5]) Bolt("M3",10,"Flat","HEX",2.5);
        translate([-MHspc/3,0,15-5]) Bolt("M3",10,"Flat","HEX",2.5);
        translate([0,0,15+26.7+15]) rotate([0,0,360/12*1])
        {
            translate([MHspc/2,MHspc/2,-15]) rotate([0,0,0])
            {
                Bolt("M3",25,"Flat","HEX",2.5);
                translate([0,0,21]) rotate([0,0,30]) Nut(size="M3", "Security");
            }
            translate([MHspc/2,-MHspc/2,-15]) rotate([0,0,0]) 
            {
                Bolt("M3",25,"Flat","HEX",2.5);
                translate([0,0,21]) rotate([0,0,30]) Nut(size="M3", "Security");
            }
            translate([-MHspc/2,MHspc/2,-15]) rotate([0,0,0]) 
            {
                Bolt("M3",25,"Flat","HEX",2.5);
                translate([0,0,21]) rotate([0,0,30]) Nut(size="M3", "Security");
            }
            translate([-MHspc/2,-MHspc/2,-15]) rotate([0,0,0]) 
            {
                Bolt("M3",25,"Flat","HEX",2.5);
                translate([0,0,21]) rotate([0,0,30]) Nut(size="M3", "Security");
            }
                //translate([0,-MHspc/3,-15+5]) rotate([180,0,0]) Bolt("M3",10,"Flat","HEX",2.5);
                //translate([0,MHspc/3,-15+5]) rotate([180,0,0]) Bolt("M3",10,"Flat","HEX",2.5);
        }
        
        rotate([0,0,-90])
        {
            color([0.2,0.2,0.2]) Adapter_Base();
                color([0.9,0.9,0.1]) Adapter_gasket();
        }
            color([0.2,0.2,0.2]) Adapter_TopCover();
        
        color([0.2,0.2,0.2]) translate([0,0,2+4.1+28.3/2+8]) Adapter_Intermediate();
            translate([0,0,2+4.1+28.3/2+8]) color([0.9,0.9,0.1]) AdapterOutput_StrainRelief();
        
        translate([0,0,2+2+4.1*2+28.3+8*2]) rotate([0,180,360/12])
        {
            color([0.2,0.2,0.2]) Adapter_Base();
                color([0.9,0.9,0.1]) Adapter_gasket();
            color([0.2,0.2,0.2]) rotate([0,0,90]) Adapter_TopCover();
            
            color([0.2,0.2,0.2]) Adapter_Cap();
        }
    }
}

module MountingPlate(powermeter=false) difference()
{
    union()
    {
        // PCB standofs
        translate([4.5,15,-ofst]) Standoff(diam=4.2+layW*4, heigh=ofst, holeSIZE="M3", holeTYPE="threadHole");
        translate([85.5,15,-ofst]) Standoff(diam=4.2+layW*4, heigh=ofst, holeSIZE="M3", holeTYPE="threadHole");
        translate([4.5,85.5,-ofst]) Standoff(diam=4.2+layW*4, heigh=ofst, holeSIZE="M3", holeTYPE="threadHole");
        
        translate([73-25/2,73-25/2,-ofst]) Standoff(diam=4.2+layW*4, heigh=ofst, holeSIZE="M3", holeTYPE="threadHole");
        for(i=[-1:2:1]) for(j=[-1:2:1]) if(i !=-1 || j != -1) translate([-100+73+i*25/2,73+j*25/2,-ofst]) Standoff(diam=4.2+layW*4, heigh=ofst, holeSIZE="M3", holeTYPE="threadHole");
        
        // base structure
        hull()
        {
            translate([4.5,15,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
            translate([85.5,15,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
            
            translate([73-25/2,73-25/2,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
            translate([-100+73-25/2,73+25/2,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
            
            translate([4.5+10,85.5+19,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=0.5,chamfB=1,thick=baseTH);
            translate([-100+73-25/2-10,73+25/2+19,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=0.5,chamfB=1,thick=baseTH);
        }
        
        if(powermeter)
        {
            translate([70,-20+(0.8*INtoMM)/2,-ofst]) Standoff(diam=4.2+layW*4, heigh=ofst, holeSIZE="M2.5", holeTYPE="threadHole");
            translate([70,-20-(0.8*INtoMM)/2,-ofst]) Standoff(diam=4.2+layW*4, heigh=ofst, holeSIZE="M2.5", holeTYPE="threadHole");
            
            translate([70-10,-20,-ofst]) Standoff(diam=2+layW*4, heigh=ofst, holeSIZE="M2.5", holeTYPE="");
            
            hull()
            {
                translate([85.5,15,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
                translate([30,15,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
                
                translate([70,-20-(0.8*INtoMM)/2,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
            }
        }
    }
    
    // bolt hole cutout
    if(!$preview)
    {
        translate([4.5,15,1]) rotate([180,0,0])
        {
            Bolt_cutout(size="M3", length=ofst+baseTH+2, insert_extention=1, type="Flat", thread=ofst+baseTH+2-5, layer=0);
            translate([0,0,ofst+baseTH-2.5]) Nut_cutout(size="M3", type="Pressfit", depth=2.5, extention=1, layer=layH);
        }
        translate([85.5,15,1]) rotate([180,0,0])
        {
            Bolt_cutout(size="M3", length=ofst+baseTH+2, insert_extention=1, type="Flat", thread=ofst+baseTH+2-5, layer=0);
            translate([0,0,ofst+baseTH-2.5]) Nut_cutout(size="M3", type="Pressfit", depth=2.5, extention=1, layer=layH);
        }
        translate([4.5,85.5,1]) rotate([180,0,0])
        {
            Bolt_cutout(size="M3", length=ofst+baseTH+2, insert_extention=1, type="Flat", thread=ofst+baseTH+2-5, layer=0);
            translate([0,0,ofst+baseTH-2.5]) Nut_cutout(size="M3", type="Pressfit", depth=2.5, extention=1, layer=layH);
        }
        
        translate([73-25/2,73-25/2,1]) rotate([180,0,0])
        {
            Bolt_cutout(size="M3", length=ofst+baseTH+2, insert_extention=1, type="Flat", thread=ofst+baseTH+2-5, layer=0);
            translate([0,0,ofst+baseTH-2.5]) Nut_cutout(size="M3", type="Pressfit", depth=2.5, extention=1, layer=layH);
        }
        for(i=[-1:2:1]) for(j=[-1:2:1]) if(i !=-1 || j != -1) translate([-100+73+i*25/2,73+j*25/2,1]) rotate([180,0,0])
        {
            Bolt_cutout(size="M3", length=ofst+baseTH+2, insert_extention=1, type="Flat", thread=ofst+baseTH+2-5, layer=0);
            translate([0,0,ofst+baseTH-2.5]) Nut_cutout(size="M3", type="Pressfit", depth=2.5, extention=1, layer=layH);
        }
        
        
        translate([70,-20+(0.8*INtoMM)/2,1]) rotate([180,0,0])
        {
            Bolt_cutout(size="M2.5", length=ofst+baseTH+2, insert_extention=1, type="Flat", thread=ofst+baseTH+2-5, layer=0);
            translate([0,0,ofst+baseTH-2.5]) Nut_cutout(size="M2.5", type="Pressfit", depth=2.5, extention=1, layer=layH);
        }
        translate([70,-20-(0.8*INtoMM)/2,1]) rotate([180,0,0])
        {
            Bolt_cutout(size="M2.5", length=ofst+baseTH+2, insert_extention=1, type="Flat", thread=ofst+baseTH+2-5, layer=0);
            translate([0,0,ofst+baseTH-2.5]) Nut_cutout(size="M2.5", type="Pressfit", depth=2.5, extention=1, layer=layH);
        }
    }

    // frame securing screw cutouts
    translate([-100+73-25/2-10,73+25/2+19,-ofst-baseTH-0.3]) Bolt_cutout(size="M3", length=baseTH+2, insert_extention=1, type="Countersink", thread=0, layer=0);
    translate([((-100+73-25/2-10)+(4.5+10))/2,85.5+19,-ofst-baseTH-0.3]) Bolt_cutout(size="M3", length=baseTH+2, insert_extention=1, type="Countersink", thread=0, layer=0);
    translate([4.5+10,85.5+19,-ofst-baseTH-0.3]) Bolt_cutout(size="M3", length=baseTH+2, insert_extention=1, type="Countersink", thread=0, layer=0);
    
    // frame material reduction
    for(l=[-1:1:1])
    {
        hull()
        {
            translate([27,22,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+2,chamf=1,thick=baseTH,part=l);
            translate([70,22,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+2,chamf=1,thick=baseTH,part=l);
            translate([55,43,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+2,chamf=1,thick=baseTH,part=l);
        }
        hull()
        {
            translate([5,35,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+1,chamf=1,thick=baseTH,part=l);
            translate([5,65,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+1,chamf=1,thick=baseTH,part=l);
            translate([25,80,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+1,chamf=1,thick=baseTH,part=l);
            translate([5+40,35+30,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+1,chamf=1,thick=baseTH,part=l);
        }
        
        hull()
        {
            translate([68,3,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+1,chamf=1,thick=baseTH,part=l);
            translate([50,3,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+1,chamf=1,thick=baseTH,part=l);
            translate([57,-5,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+1,chamf=1,thick=baseTH,part=l);
        }
    }
}
    module MountingPlate_edge() difference()
    {
        union()
        {
            // PCB standofs
            for(i=[-1:2:1]) for(j=[-1:2:1]) if(i !=-1 || j != -1) translate([-100+73+i*25/2,73+j*25/2,-ofst]) Standoff(diam=6, heigh=ofst, holeSIZE="M3", holeTYPE="Thread");
            
            // base structure
            hull()
            {
                for(i=[-1:2:1]) for(j=[-1:2:1]) if(i !=-1 || j != -1) translate([-100+73+i*25/2,73+j*25/2,-ofst-baseTH/2]) ChamferedPuck(diam=9+2,chamfT=2,chamfB=1,thick=baseTH);
                
                translate([-100+73+25/2-5,73+25/2+19,-ofst-baseTH/2]) ChamferedPuck(diam=9+2,chamfT=0.5,chamfB=1,thick=baseTH);
                translate([-100+73-25/2-10,73+25/2+19,-ofst-baseTH/2]) ChamferedPuck(diam=9+2,chamfT=0.5,chamfB=1,thick=baseTH);
            }
        }
        
        // bolt hole cutout
        if(!$preview) for(i=[-1:2:1]) for(j=[-1:2:1]) if(i !=-1 || j != -1) translate([-100+73+i*25/2,73+j*25/2,1]) rotate([180,0,0])
    {
        Bolt_cutout(size="M3", length=ofst+baseTH+2, insert_extention=1, type="Flat", thread=ofst+baseTH+2-5, layer=0);
        translate([0,0,ofst+baseTH-2.5]) Nut_cutout(size="M3", type="Pressfit", depth=2.5, extention=1, layer=layH);
    }
            
        // frame securing screw cutouts
        translate([-100+73-25/2-10,73+25/2+19,-ofst-baseTH-0.3]) Bolt_cutout(size="M3", length=baseTH+2, insert_extention=1, type="Countersink", thread=0, layer=0);
        translate([-100+73+25/2-5,85.5+19,-ofst-baseTH-0.3]) Bolt_cutout(size="M3", length=baseTH+2, insert_extention=1, type="Countersink", thread=0, layer=0);
    }

module MountingPlate_RPi() difference()
{
    union()
    {
        // PCB standofs
        translate([4.5,15,-ofst]) Standoff(diam=4.2+layW*4, heigh=ofst, holeSIZE="M3", holeTYPE="threadHole");
        translate([85.5,15,-ofst]) Standoff(diam=4.2+layW*4, heigh=ofst, holeSIZE="M3", holeTYPE="threadHole");
        translate([4.5,85.5,-ofst]) Standoff(diam=4.2+layW*4, heigh=ofst, holeSIZE="M3", holeTYPE="threadHole");
            translate([73-25/2,73-25/2,-ofst]) Standoff(diam=4.2+layW*4, heigh=ofst, holeSIZE="M3", holeTYPE="threadHole");
        
        // RPi standofs
        translate([-40+49/2,30+85/2-3.5,-ofst]) Standoff(diam=4.2+layW*4, heigh=ofst, holeSIZE="M2.5", holeTYPE="threadHole");
        translate([-40+49/2,30+85/2-3.5-58,-ofst]) Standoff(diam=4.2+layW*4, heigh=ofst, holeSIZE="M2.5", holeTYPE="threadHole");
        
        // base structure
        hull()
        {
            translate([4.5,15,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
            translate([4.5,85.5,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
            translate([85.5,15,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
                translate([73-25/2,73-25/2,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
            
            translate([73-25/2-25,73-25/2+25,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
        }
            // RPi plate
            hull()
            {
                translate([73-25/2-100,73-25/2+25,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
                translate([4.5,15,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
                translate([4.5,85.5,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
                
                translate([-40+49/2,30+85/2-3.5-58,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
            }
            // DCDC buck plate
            hull()
            {
                translate([22,-27,-ofst-baseTH/2]) ChamferedPuck(diam=6,chamfT=2,chamfB=1,thick=baseTH);
                translate([-25,-27,-ofst-baseTH/2]) ChamferedPuck(diam=6,chamfT=2,chamfB=1,thick=baseTH);
                
                translate([22,-3,-ofst-baseTH/2]) ChamferedPuck(diam=6,chamfT=2,chamfB=1,thick=baseTH);
                translate([-25,-3,-ofst-baseTH/2]) ChamferedPuck(diam=6,chamfT=2,chamfB=1,thick=baseTH);
                
                translate([35,10,-ofst-baseTH/2]) ChamferedPuck(diam=6,chamfT=2,chamfB=1,thick=baseTH);
                translate([-20,15,-ofst-baseTH/2]) ChamferedPuck(diam=6,chamfT=2,chamfB=1,thick=baseTH);
            }
                // securing structure
                difference()
                {
                    hull()
                    {
                        translate([22,-27,-ofst]) cylinder(d1=6-2, d2=1, h=0.5+1.6+0.4);
                        translate([-25,-27,-ofst]) cylinder(d1=6-2, d2=1, h=0.5+1.6+0.4);
                        translate([22,-3,-ofst]) cylinder(d1=6-2, d2=1, h=0.5+1.6+0.4);
                        translate([-25,-3,-ofst]) cylinder(d1=6-2, d2=1, h=0.5+1.6+0.4);
                    }
                    
                    difference()
                    {
                        union()
                        {
                            // top cutout
                            translate([-2,-15,3.5/2-ofst+0.5]) cube([43.5-1,20.4-1,3.5], center=true);
                            // slot
                            hull()
                            {
                                translate([-2-5/2,-15,1.6/2-ofst+0.5]) cube([43.5+1+5,20.4+1,1.57-1], center=true);
                                translate([-2-5/2,-15,1.6/2-ofst+0.5]) cube([43.5-1+5,20.4-1,1.57+1], center=true);
                            }
                        }
                        
                        // securing tab
                        difference()
                        {
                            translate([-25,-15,-5]) cube([10,5,10], center=true);
                            
                            translate([1,0,0]) hull()
                            {
                                translate([-2,-15,1.6/2-ofst+0.5]) cube([43.5+1,20.4+1,1.57-1], center=true);
                                translate([-2,-15,1.6/2-ofst+0.5]) cube([43.5-1,20.4-1,1.57+1], center=true);
                            }
                        }
                    }
                }
        hull()
        {
            translate([73-25/2-25,73-25/2+25,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
                translate([73-25/2-100,73-25/2+25,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
            
            translate([4.5+10,85.5+19,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=0.5,chamfB=1,thick=baseTH);
            translate([-100+73-25/2-10,73+25/2+19,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=0.5,chamfB=1,thick=baseTH);
        }
    }
    
    // bolt hole cutout
    if(!$preview)
    {
        translate([-40+49/2,30+85/2-3.5,-(ofst+baseTH)+2]) Bolt_cutout(size="M2.5", length=10, insert_extention=2.2, type="HEX", thread=0, layer=0.2);
        translate([-40+49/2,30+85/2-3.5-58,-(ofst+baseTH)+2]) Bolt_cutout(size="M2.5", length=10, insert_extention=2.2, type="HEX", thread=0, layer=0.2);
        
        translate([4.5,15,1]) rotate([180,0,0])
        {
            Bolt_cutout(size="M3", length=ofst+baseTH+2, insert_extention=1, type="Flat", thread=ofst+baseTH+2-5, layer=0);
            translate([0,0,ofst+baseTH-2.5]) Nut_cutout(size="M3", type="Pressfit", depth=2.5, extention=1, layer=layH);
        }
        translate([85.5,15,1]) rotate([180,0,0])
        {
            Bolt_cutout(size="M3", length=ofst+baseTH+2, insert_extention=1, type="Flat", thread=ofst+baseTH+2-5, layer=0);
            translate([0,0,ofst+baseTH-2.5]) Nut_cutout(size="M3", type="Pressfit", depth=2.5, extention=1, layer=layH);
        }
        translate([4.5,85.5,1]) rotate([180,0,0])
        {
            Bolt_cutout(size="M3", length=ofst+baseTH+2, insert_extention=1, type="Flat", thread=ofst+baseTH+2-5, layer=0);
            translate([0,0,ofst+baseTH-2.5]) Nut_cutout(size="M3", type="Pressfit", depth=2.5, extention=1, layer=layH);
        }
        
        translate([73-25/2,73-25/2,1]) rotate([180,0,0])
        {
            Bolt_cutout(size="M3", length=ofst+baseTH+2, insert_extention=1, type="Flat", thread=ofst+baseTH+2-5, layer=0);
            translate([0,0,ofst+baseTH-2.5]) Nut_cutout(size="M3", type="Pressfit", depth=2.5, extention=1, layer=layH);
        }
    }
    
    // DCDC latching spring cutout
    translate([-15,-15,-5]) difference()
    {
        hull()
        {
            translate([-4/2+3.5,-10/2+4/2,0]) cylinder(d=4, h=10, center=true);
            translate([-8/2+3.5,10/2-8/2,0]) cylinder(d=8, h=10, center=true);
            
            translate([-20,0,0]) cube([1,10,10], center=true);
        }
        
        translate([-10,0,0]) hull()
        {
            translate([7/2-3/2,2,0]) cylinder(d=3, h=10, center=true);
            translate([7/2-3/2,-2,0]) cylinder(d=3, h=10, center=true);
            translate([-1.8,2,0]) cylinder(d=3, h=10, center=true);
            translate([-1.8,-2,0]) cylinder(d=3, h=10, center=true);
        }
        
        translate([-10+7/2,0,-3]) linear_extrude(10) Spring(curveD=6,springTH=0.45*4,length=10,startW=9,endW=9);
    }
                            
    // frame securing screw cutouts
    translate([-100+73-25/2-10,73+25/2+19,-ofst-baseTH-0.3]) Bolt_cutout(size="M3", length=baseTH+2, insert_extention=1, type="Countersink", thread=0, layer=0);
    translate([((-100+73-25/2-10)+(4.5+10))/2,85.5+19,-ofst-baseTH-0.3]) Bolt_cutout(size="M3", length=baseTH+2, insert_extention=1, type="Countersink", thread=0, layer=0);
    translate([4.5+10,85.5+19,-ofst-baseTH-0.3]) Bolt_cutout(size="M3", length=baseTH+2, insert_extention=1, type="Countersink", thread=0, layer=0);
    
    // frame material reduction
    for(l=[-1:1:1])
    {
        hull()
        {
            translate([27,22,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+2,chamf=1,thick=baseTH,part=l);
            translate([70,22,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+2,chamf=1,thick=baseTH,part=l);
            translate([55,43,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+2,chamf=1,thick=baseTH,part=l);
        }
        hull()
        {
            translate([5,35,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+1,chamf=1,thick=baseTH,part=l);
            translate([5,65,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+1,chamf=1,thick=baseTH,part=l);
            translate([25,80,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+1,chamf=1,thick=baseTH,part=l);
            translate([5+40,35+30,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+1,chamf=1,thick=baseTH,part=l);
        }
        hull()
        {
            translate([-12,25,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+1,chamf=1,thick=baseTH,part=l);
            translate([-12,55,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+1,chamf=1,thick=baseTH,part=l);
            translate([-19,52,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+1,chamf=1,thick=baseTH,part=l);
        }
        hull()
        {
            translate([-10,82,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+1,chamf=1,thick=baseTH,part=l);
            translate([-30,82,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+1,chamf=1,thick=baseTH,part=l);
            translate([-20,90,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+1,chamf=1,thick=baseTH,part=l);
        }
        
        hull()
        {
            translate([23,4,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=6+1,chamf=1,thick=baseTH,part=l);
            translate([-5,4,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=6+1,chamf=1,thick=baseTH,part=l);
        }
    }
}

module MountingPlate_RPi_edge() difference()
{
    union()
    {
        // PCB standofs
        translate([100-40-49/2,30+85/2-3.5,-ofst]) Standoff(diam=4.2+layW*4, heigh=ofst, holeSIZE="M2.5", holeTYPE="threadHole");
        translate([100-40-49/2,30+85/2-3.5-58,-ofst]) Standoff(diam=4.2+layW*4, heigh=ofst, holeSIZE="M2.5", holeTYPE="threadHole");
        
        translate([100-40-49/2-23,30+85/2-3.5,-ofst]) Standoff(diam=4.2+layW*4, heigh=ofst, holeSIZE="M2.5", holeTYPE="threadHole");
        translate([100-40-49/2-23,30+85/2-3.5-58,-ofst]) Standoff(diam=4.2+layW*4, heigh=ofst, holeSIZE="M2.5", holeTYPE="threadHole");
        
        // base structure
        hull()
        {
            translate([100-40-49/2,30+85/2-3.5,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
            translate([0,30+85/2-3.5,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
            translate([100-40-49/2-23,30+85/2-3.5-58,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
            translate([100-40-49/2,30+85/2-3.5-58,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
        }
        hull()
        {
            translate([100-40-49/2,30+85/2-3.5,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
            translate([0,30+85/2-3.5,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
            
            translate([-20,73+25/2+19,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=0.5,chamfB=1,thick=baseTH);
            translate([30,73+25/2+19,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=0.5,chamfB=1,thick=baseTH);
        }
    }
    
    // antenna cutout
    translate([20,87,-ofst]) intersection()
    {
        cylinder(d=1/4*INtoMM+tol*4, h=10, center=true);
        translate([-(1/4*INtoMM+tol*4)/2-(1/4*INtoMM+tol*4)/2+5.8+tol*2,0,0]) cube([1/4*INtoMM+tol*4,1/4*INtoMM+tol*4,10.1], center=true);
    }
        translate([20-4,87-6,-ofst-0.4]) linear_extrude(1) text("GNSS", size=5.5, halign="left", valign="top");
        translate([20-4,87-6,-ofst-baseTH+0.4]) rotate([0,180,0]) linear_extrude(1) text("GNSS", size=5.5, halign="right", valign="top");
    translate([0,87,-ofst]) intersection()
    {
        cylinder(d=1/4*INtoMM+tol*4, h=10, center=true);
        translate([-(1/4*INtoMM+tol*4)/2-(1/4*INtoMM+tol*4)/2+5.8+tol*2,0,0]) cube([1/4*INtoMM+tol*4,1/4*INtoMM+tol*4,10.1], center=true);
    }
        translate([0-8,87-6,-ofst-0.4]) linear_extrude(1) text("main", size=5.5, halign="left", valign="top");
        translate([0-8,87-6,-ofst-baseTH+0.4]) rotate([0,180,0]) linear_extrude(1) text("main", size=5.5, halign="right", valign="top");
    
    // bolt hole cutout
    if(!$preview)
    {
        translate([100-40-49/2,30+85/2-3.5,-(ofst+baseTH)+2]) Bolt_cutout(size="M2.5", length=10, insert_extention=2.2, type="HEX", thread=0, layer=0.2);
        translate([100-40-49/2,30+85/2-3.5-58,-(ofst+baseTH)+2]) Bolt_cutout(size="M2.5", length=10, insert_extention=2.2, type="HEX", thread=0, layer=0.2);
        
        translate([100-40-49/2-23,30+85/2-3.5,-(ofst+baseTH)+2]) Bolt_cutout(size="M2.5", length=10, insert_extention=2.2, type="HEX", thread=0, layer=0.2);
        translate([100-40-49/2-23,30+85/2-3.5-58,-(ofst+baseTH)+2]) Bolt_cutout(size="M2.5", length=10, insert_extention=2.2, type="HEX", thread=0, layer=0.2);
    }

    // frame securing screw cutouts
    translate([-20,73+25/2+19,-ofst-baseTH-0.3]) Bolt_cutout(size="M3", length=baseTH+2, insert_extention=1, type="Countersink", thread=0, layer=0);
    translate([30,73+25/2+19,-ofst-baseTH-0.3]) Bolt_cutout(size="M3", length=baseTH+2, insert_extention=1, type="Countersink", thread=0, layer=0);
    
    // frame material reduction
    for(l=[-1:1:1])
    {
        hull()
        {
            translate([24,58,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+2,chamf=1,thick=baseTH,part=l);
            translate([24,20,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+2,chamf=1,thick=baseTH,part=l);
        }
        
    }
}

module USB_holder() difference()
{
    union()
    {
        // front plate
        hull() for(i=[-1:2:1]) for(j=[0:1:1]) for(k=[0:1:1]) translate([i*(25/2-2/2),2/2+j*(35-2/2),2/2]) sphere(d=2);
        
        // atachment wings
        for(i=[0:1:1]) mirror([i,0,0]) hull()
        {
            translate([25/2-2/2,35-2/2+2/2,2/2]) sphere(d=2);
                translate([20/2+2/2,35-2/2+2/2,2/2]) sphere(d=2);
            translate([20/2+2/2,-2/2,2/2]) sphere(d=2);
                translate([20/2+2/2,-10+2/2,2/2]) sphere(d=2);
            translate([25/2-2/2,-2/2-7,2/2]) sphere(d=2);
            
            translate([20/2+2/2,-10+2/2,24]) sphere(d=2);
                translate([20/2+2/2,-2/2,24]) sphere(d=2);
            translate([25/2-2/2,-2/2-7,23]) sphere(d=2);
                translate([25/2-2/2,-2/2,23]) sphere(d=2);
        }
        
        // reinforcement wings
    }
    
    hull() for(i=[-1:2:1]) for(j=[-1:2:1]) translate([i*(12.75/2-2/2),35/2+j*(26/2-2/2),1/2]) cylinder(d=2, h=1.1, center=true);
    hull() for(i=[-1:2:1]) for(j=[-1:2:1]) translate([i*(12.75/2-2/2),35/2+j*(30/2-2/2),1]) cylinder(d=2, h=10);
    
    // atashment bolt cutout
    translate([25/2+0.5,-10/2,24*1/3]) rotate([0,-90,0]) Bolt_cutout(size="M3", length=baseTH+2, insert_extention=1, type="sCountersink", thread=0, layer=0);
    translate([-25/2-0.5,-10/2,24*2/3]) rotate([0,90,0]) rotate([0,0,180]) Bolt_cutout(size="M3", length=baseTH+2, insert_extention=1, type="sCountersink", thread=0, layer=0);
    
    translate([0,8/2,2/2]) cube([3,10,2.1], center=true);
}
    module USB_UARTadapter_holder() difference()
    {
        union()
        {
            // front plate
            hull() for(i=[-1:2:1]) for(j=[0:1:1]) for(k=[0:1:1]) translate([i*(25/2-2/2),2/2+j*(35-2/2),2/2]) sphere(d=2);
            
            // atachment wings
            for(i=[0:1:1]) mirror([i,0,0]) hull()
            {
                translate([25/2-2/2,35-2/2+2/2,2/2]) sphere(d=2);
                    translate([20/2+2/2,35-2/2+2/2,2/2]) sphere(d=2);
                translate([20/2+2/2,-2/2,2/2]) sphere(d=2);
                    translate([20/2+2/2,-10+2/2,2/2]) sphere(d=2);
                translate([25/2-2/2,-2/2-7,2/2]) sphere(d=2);
                
                translate([20/2+2/2,-10+2/2,24]) sphere(d=2);
                    translate([20/2+2/2,-2/2,24]) sphere(d=2);
                translate([25/2-2/2,-2/2-7,23]) sphere(d=2);
                    translate([25/2-2/2,-2/2,23]) sphere(d=2);
            }
            
            // reinforcement wings
        }
        
        hull() for(i=[-1:2:1]) for(j=[-1:2:1]) translate([i*(9/2-1/2),35/2+j*(23/2-1/2),3/2]) cylinder(d=1, h=3.1, center=true);
        //hull() for(i=[-1:2:1]) for(j=[-1:2:1]) translate([i*(12.75/2-2/2),35/2+j*(30/2-2/2),1]) cylinder(d=2, h=10);
        
        // atashment bolt cutout
        translate([25/2+0.5,-10/2,24*1/3]) rotate([0,-90,0]) Bolt_cutout(size="M3", length=baseTH+2, insert_extention=1, type="sCountersink", thread=0, layer=0);
        translate([-25/2-0.5,-10/2,24*2/3]) rotate([0,90,0]) rotate([0,0,180]) Bolt_cutout(size="M3", length=baseTH+2, insert_extention=1, type="sCountersink", thread=0, layer=0);
        
        translate([0,8/2,2/2]) cube([3,10,2.1], center=true);
    }

// ======================= Alternatives
module MountingPlate_RPiZero() difference()
{
    union()
    {
        // PCB standofs
        translate([-60-23/2,40+58/2,-ofst]) Standoff(diam=6, heigh=ofst, holeSIZE="M2.5", holeTYPE="threadHole");
        translate([-60+23/2,40+58/2,-ofst]) Standoff(diam=6, heigh=ofst, holeSIZE="M2.5", holeTYPE="threadHole");
        translate([-60-23/2,40-58/2,-ofst]) Standoff(diam=6, heigh=ofst, holeSIZE="M2.5", holeTYPE="threadHole");
        translate([-60+23/2,40-58/2,-ofst]) Standoff(diam=6, heigh=ofst, holeSIZE="M2.5", holeTYPE="threadHole");
        
        
        // base structure
        hull()
        {
            translate([-40,85.5+19,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=0.5,chamfB=1,thick=baseTH);
            translate([-40-35*2,85.5+19,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=0.5,chamfB=1,thick=baseTH);
            
            translate([-60-23/2-10,40+58/2,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
            translate([-60+23/2,40+58/2,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
        }
        hull()
        {
            translate([-60-23/2-10,40+58/2,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
            translate([-60+23/2,40+58/2,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
            
            translate([-60-23/2,40-58/2,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
            translate([-60+23/2,40-58/2,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
        }
    }
    
    // frame securing screw cutouts
    translate([-40,85.5+19,-ofst-baseTH-0.3]) Bolt_cutout(size="M3", length=baseTH+2, insert_extention=1, type="Countersink", thread=0, layer=0);
    translate([-40-35,85.5+19,-ofst-baseTH-0.3]) Bolt_cutout(size="M3", length=baseTH+2, insert_extention=1, type="Countersink", thread=0, layer=0);
    translate([-40-35*2,85.5+19,-ofst-baseTH-0.3]) Bolt_cutout(size="M3", length=baseTH+2, insert_extention=1, type="Countersink", thread=0, layer=0);
}

module MountingPlate_first()difference()
{
    union()
    {
        // PCB standofs
        translate([4.5,15,-ofst]) Standoff(diam=4.2+layW*4, heigh=ofst, holeSIZE="M3", holeTYPE="threadHole");
        translate([85.5,15,-ofst]) Standoff(diam=4.2+layW*4, heigh=ofst, holeSIZE="M3", holeTYPE="threadHole");
        translate([4.5,85.5,-ofst]) Standoff(diam=4.2+layW*4, heigh=ofst, holeSIZE="M3", holeTYPE="threadHole");
        
        translate([73-25/2,73-25/2,-ofst]) Standoff(diam=4.2+layW*4, heigh=ofst, holeSIZE="M3", holeTYPE="threadHole");
        
        // base structure
        hull()
        {
            translate([4.5,15,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
            translate([85.5,15,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
            
            translate([73-25/2,73-25/2,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
        
            translate([73-25/2,73-25/2,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
            translate([4.5,85.5,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
            
            translate([4.5+10,85.5+19,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=0.5,chamfB=1,thick=baseTH);
        }
        hull()
        {
            translate([5,70,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=2,chamfB=1,thick=baseTH);
            translate([((-100+73-25/2-10)+(4.5+10))/2,85.5+19,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=0.5,chamfB=1,thick=baseTH);
            translate([4.5+10,85.5+19,-ofst-baseTH/2]) ChamferedPuck(diam=(4.2+layW*4)+3+2,chamfT=0.5,chamfB=1,thick=baseTH);
        }
    }
    
    // bolt hole cutout
    if(!$preview)
    {
        translate([-15,70-23,1]) rotate([180,0,0])
        {
            Bolt_cutout(size="M2.5", length=ofst+baseTH+2, insert_extention=1, type="Flat", thread=ofst+baseTH+2-5, layer=0);
            translate([0,0,ofst+baseTH-2.5]) Nut_cutout(size="M2.5", type="Pressfit", depth=2.5, extention=1, layer=layH);
        }
        translate([4.5,15,1]) rotate([180,0,0])
        {
            Bolt_cutout(size="M3", length=ofst+baseTH+2, insert_extention=1, type="Flat", thread=ofst+baseTH+2-5, layer=0);
            translate([0,0,ofst+baseTH-2.5]) Nut_cutout(size="M3", type="Pressfit", depth=2.5, extention=1, layer=layH);
        }
        translate([85.5,15,1]) rotate([180,0,0])
        {
            Bolt_cutout(size="M3", length=ofst+baseTH+2, insert_extention=1, type="Flat", thread=ofst+baseTH+2-5, layer=0);
            translate([0,0,ofst+baseTH-2.5]) Nut_cutout(size="M3", type="Pressfit", depth=2.5, extention=1, layer=layH);
        }
        translate([4.5,85.5,1]) rotate([180,0,0])
        {
            Bolt_cutout(size="M3", length=ofst+baseTH+2, insert_extention=1, type="Flat", thread=ofst+baseTH+2-5, layer=0);
            translate([0,0,ofst+baseTH-2.5]) Nut_cutout(size="M3", type="Pressfit", depth=2.5, extention=1, layer=layH);
        }
        
        translate([73-25/2,73-25/2,1]) rotate([180,0,0])
        {
            Bolt_cutout(size="M3", length=ofst+baseTH+2, insert_extention=1, type="Flat", thread=ofst+baseTH+2-5, layer=0);
            translate([0,0,ofst+baseTH-2.5]) Nut_cutout(size="M3", type="Pressfit", depth=2.5, extention=1, layer=layH);
        }
    }

    // frame securing screw cutouts
    translate([((-100+73-25/2-10)+(4.5+10))/2,85.5+19,-ofst-baseTH-0.3]) Bolt_cutout(size="M3", length=baseTH+2, insert_extention=1, type="Countersink", thread=0, layer=0);
    translate([4.5+10,85.5+19,-ofst-baseTH-0.3]) Bolt_cutout(size="M3", length=baseTH+2, insert_extention=1, type="Countersink", thread=0, layer=0);
    
    // frame material reduction
    for(l=[-1:1:1])
    {
        hull()
        {
            translate([27,22,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+2,chamf=1,thick=baseTH,part=l);
            translate([70,22,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+2,chamf=1,thick=baseTH,part=l);
            translate([55,43,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+2,chamf=1,thick=baseTH,part=l);
        }
        hull()
        {
            translate([12,38,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+1,chamf=1,thick=baseTH,part=l);
            translate([12,65,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+1,chamf=1,thick=baseTH,part=l);
            translate([26,82,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+1,chamf=1,thick=baseTH,part=l);
            translate([42,35+30,-ofst-baseTH/2]) ChamferedPuck_cutout(diam=9+1,chamf=1,thick=baseTH,part=l);
        }
    }
}