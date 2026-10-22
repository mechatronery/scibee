include <Hardware.scad>
include <datasheet/muRata_pump.scad>
include <Structure.scad>


/* [Parameters] */
// Pump model number
PUMPmodel="MZB3004T04";  // ["MZB3005T06","MZB1001T02","MZB3004T04"]
// Pump number
PUMPno=2;       // [1:1:2]
// Tools
TUBEtool=false;
FILTERtool=false;

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
$fn= $preview ? 60 : 180;
// pump adapter mounting hole spacing
MHspc=(85.5-60.5);
// pump output tube routing dimentions
    Td=5;   // tube diameter
Br=6;   // tube bend radius
Ba=80;  // tube bend angle


if($preview && false)
{
    color([0.1,0.7,0.1]) translate([-73,-73,-1.55]) import("SCIBee_v1.11B.stl");
        color([0.1,0.7,0.1,0.3]) translate([-73+100,-73,-1.55]) import("SCIBee_v1.11B.stl");
    if(PUMPno==1) translate([0,0,2])
    {
        // pumps
        if(PUMPmodel == "MZB3005T06") MZB3005T06();
        if(PUMPmodel == "MZB1001T02") MZB1001T02();
        if(PUMPmodel == "MZB3004T04") MZB3004T04();
        
        // hardware
        translate([MHspc/2,MHspc/2,25-10]) rotate([180,0,0]) Bolt(size="M3", length=25, type="Flat");
        translate([MHspc/2,-MHspc/2,25-10]) rotate([180,0,0]) Bolt(size="M3", length=25, type="Flat");
        translate([-MHspc/2,MHspc/2,25-10]) rotate([180,0,0]) Bolt(size="M3", length=25, type="Flat");
        translate([-MHspc/2,-MHspc/2,25-10]) rotate([180,0,0]) Bolt(size="M3", length=25, type="Flat");
        
        // structures
        color([0.5,0.5,0.5]) Adapter_Base();
        color([0.3,0.3,0.3]) Adapter_Intermediate();
        color([0.4,0.4,0.4]) Adapter_TopCover();
    }
    if(PUMPno==2)
    {
        // pump models
        if(PUMPmodel == "MZB3005T06") MZB3005T06();
        if(PUMPmodel == "MZB1001T02") MZB1001T02();
        if(PUMPmodel == "MZB3004T04") translate([0,0,0]) rotate([0,0,0])
        {
            translate([0,0,2.1]) rotate([0,0,-90]) MZB3004T04();
            translate([0,0,2+4.1+28.3/2+8]) rotate([0,90,-360/12*4]) Tjoint();
            //translate([0,0,2+4.1*2+28.3+8*2]) rotate([0,180,360/12]) MZB3004T04();
        }
        
        // hardware 
        translate([MHspc/2,MHspc/2,25-10]) rotate([180,0,0]) Bolt("M3",25,"Flat","HEX",2.5);
        translate([MHspc/2,-MHspc/2,25-10]) rotate([180,0,0]) Bolt("M3",25,"Flat","HEX",2.5);
        translate([-MHspc/2,MHspc/2,25-10]) rotate([180,0,0]) Bolt("M3",25,"Flat","HEX",2.5);
        translate([-MHspc/2,-MHspc/2,25-10]) rotate([180,0,0]) Bolt("M3",25,"Flat","HEX",2.5);
            translate([MHspc/3,0,15-5]) Bolt("M3",10,"Flat","HEX",2.5);
            translate([-MHspc/3,0,15-5]) Bolt("M3",10,"Flat","HEX",2.5);
        
        if(false) translate([0,0,15+26.7+15]) rotate([0,0,360/12*1])
        {
            translate([MHspc/2,MHspc/2,-15]) rotate([0,0,0]) Bolt("M3",25,"Flat","HEX",2.5);
            translate([MHspc/2,-MHspc/2,-15]) rotate([0,0,0]) Bolt("M3",25,"Flat","HEX",2.5);
            translate([-MHspc/2,MHspc/2,-15]) rotate([0,0,0]) Bolt("M3",25,"Flat","HEX",2.5);
            translate([-MHspc/2,-MHspc/2,-15]) rotate([0,0,0]) Bolt("M3",25,"Flat","HEX",2.5);
                translate([0,-MHspc/3,-15+5]) rotate([180,0,0]) Bolt("M3",10,"Flat","HEX",2.5);
                translate([0,MHspc/3,-15+5]) rotate([180,0,0]) Bolt("M3",10,"Flat","HEX",2.5);
        }
        
        // structures
        rotate([0,0,-90])
        {
            color([0.5,0.5,0.5]) Adapter_Base();
                color([0.9,0.9,0.9]) Adapter_gasket();
        }
            color([0.4,0.4,0.4]) Adapter_TopCover();
        
        color([0.3,0.3,0.3]) translate([0,0,2+4.1+28.3/2+8]) Adapter_Intermediate();
            translate([0,0,2+4.1+28.3/2+8]) AdapterOutput_StrainRelief();
        
        if(false) translate([0,0,2+2+4.1*2+28.3+8*2]) rotate([0,180,360/12])
        {
            color([0.5,0.5,0.5]) Adapter_Base();
                color([0.9,0.9,0.9]) Adapter_gasket();
            color([0.4,0.4,0.4]) rotate([0,0,90]) Adapter_TopCover();
            
            color([0.4,0.4,0.4]) Adapter_Cap();
        }
    }
    
    if(PUMPno==2 && TUBEtool)
    {
        rotate([0,0,-360/12*4]) TubeTool();
        
        rotate([0,0,-360/12*4]) translate([-20,0,6.3-1+(16+5)]) Bolt(size="M3", length=15, Headtype="Countersink", driverType="HEX", driverSize=2.5);
    }
    
    if(FILTERtool) translate([0,0,56.5+2/2]) rotate([0,0,30]) filter_CutTool();
}
else
{
    
}


// ===== ===== Structures ===== =====
// multipump structures
module Adapter_Base() difference()
{
    union()
    {
        if(PUMPmodel == "MZB3004T04")
        {
            hull()
            {
                translate([MHspc/2,MHspc/2,0]) cylinder(d=6, h=2+3.4);
                translate([MHspc/2,-MHspc/2,0]) cylinder(d=6, h=2+3.4);
                translate([-MHspc/2,MHspc/2,0]) cylinder(d=6, h=2+3.4);
                translate([-MHspc/2,-MHspc/2,0]) cylinder(d=6, h=2+3.4);
            }
        }
    }
    
    if(PUMPmodel == "MZB3004T04")
    {
        // pump cutout
        hull()
        {
            translate([19/2-1/2,19/2-1/2,-3+2+3.4-1]) cylinder(d=1, h=3.1);
            translate([19/2-1/2,-19/2+1/2,-3+2+3.4-1]) cylinder(d=1, h=3.1);
            translate([-19/2+1/2,19/2-1/2,-3+2+3.4-1]) cylinder(d=1, h=3.1);
            translate([-19/2+1/2,-19/2+1/2,-3+2+3.4-1]) cylinder(d=1, h=3.1);
        }
        hull()
        {
            translate([21/2+tol-1/2,19/2-1/2+tol,2+3.4-1]) cylinder(d=1, h=2);
            translate([21/2+tol-1/2,-19/2+1/2-tol,2+3.4-1]) cylinder(d=1, h=2);
            translate([-21/2-tol+1/2,19/2-1/2+tol,2+3.4-1]) cylinder(d=1, h=2);
            translate([-21/2-tol+1/2,-19/2+1/2-tol,2+3.4-1]) cylinder(d=1, h=2);
        }
        
        // pump inlet cutout
        cylinder(d1=15, d2=18, h=2);
        // pump inlet filter cutout
        /*difference()
        {
            translate([0,0,-0.1]) cylinder(d2=24+layW*4, d1=24+layW*4+0.9*2, h=0.9);
            translate([0,0,-0.15]) cylinder(d1=18+layW*4, d2=18+layW*4+1*2, h=1);
        }*/
        
        // solder tab cutout
        translate([-21/2+6+6/2,-11,5/2+2+0.5]) cube([9,3,5], center=true);
        hull()
        {
            translate([-21/2+6,-11,2+0.5+0.45+1/2]) rotate([90,0,0])
            {
                cylinder(d=1.4, h=5);
                translate([0,2,0]) cylinder(d=1.4, h=5);
            }
            translate([-21/2+6+6,-11,2+0.5+0.45+1/2]) rotate([90,0,0])
            {
                cylinder(d=1.4, h=5);
                translate([0,2,0]) cylinder(d=1.4, h=5);
            }
        }
            // wire gasket cutout
        hull()
        {
            translate([-21/2+6-2,-12.5+tol/2,2+0.5+0.45+1/2-1.5]) rotate([90,0,0]) cylinder(d=1+tol, h=2+tol);
            translate([-21/2+6+6+2,-12.5+tol/2,2+0.5+0.45+1/2-1.5]) rotate([90,0,0]) cylinder(d=1+tol, h=2+tol);
            
            translate([-21/2+6+6/2,-2/2-12.5,5]) cube([6+2*2+1,2,1], center=true);
        }
    }
    
    MountingBolt_cutout(leng=25, lay=layH);
}
module Adapter_Intermediate() difference()
{
    if(PUMPmodel == "MZB3004T04")
    {
        hull() for(i=[0:1:6-1]) rotate([0,0,i*360/6])
        {
            translate([-MHspc/2.5,0,-26.7/2]) cylinder(d1=6-0.5, d2=6, h=0.5);
            translate([-MHspc/2.5,0,26.7/2-0.5]) cylinder(d2=6-0.5, d1=6, h=0.5);
        }
    }
    
    translate([0,0,0]) cylinder(d=Td+tol, h=8.7*2+28.3, center=true);
    translate([0,0,0]) cylinder(d=8.5, h=28, center=true);
    translate([0,0,0]) rotate([90,0,-360/12])
    {
        hull()
        {
            cylinder(d=8.5, h=20);
            translate([0,0,20/2]) cube([2,9,20], center=true);
        }
        hull()
        {
            cylinder(d=6, h=20);
            translate([0,20,0]) cylinder(d=6, h=20);
        }
    }
    
    for(i=[0:1:6-1]) rotate([0,0,i*360/6])
    {
        translate([-MHspc/3,0,-26.7/2-1.2]) Bolt_cutout(size="M3", length=14, insert_extention=4, type="Flat", thread=16, layer=layH);
        translate([-MHspc/3,0,26.7/2+1.2]) rotate([180,0,0]) Bolt_cutout(size="M3", length=14, insert_extention=4, type="Flat", thread=16, layer=layH);
    }
}
    module AdapterOutput_StrainRelief() difference()
    {
        rotate([0,0,-30]) translate([0,-4,0]) rotate([90,0,0])
        {
            hull()
            {
                cylinder(d=8.5-tol*3, h=7);
                translate([0,0,7/2]) cube([2,9-tol*3,7], center=true);
                cylinder(d=5+layW*4, h=25);
            }
            hull()
            {
                cylinder(d=6-tol*3, h=7);
                translate([0,10,0]) cylinder(d=6-tol*3, h=7);
            }
        }
        
        rotate([0,0,-30]) translate([0,-4+1,0]) rotate([90,0,0])
        {
            hull()
            {
                cylinder(d=6.5, h=8);
                cylinder(d=5, h=9);
            }
            cylinder(d=5, h=27);
        }
        
        //rotate([0,0,-30]) for(i=[0:1:12]) translate([0,-15-i*0.9,0]) rotate([0,i*40,0]) scale([1,2,1]) cylinder(d=2, h=10, center=true, $fn=4);
    }
module Adapter_TopCover() difference()
{
    if(PUMPmodel == "MZB3004T04")
    {
        for(i=[0:1:4-1]) rotate([0,0,i*90]) hull()
        {
            translate([MHspc/2,MHspc/2,2+3.4+layH*7]) cylinder(d=6, h=1);
            translate([MHspc/2,MHspc/2,-10+25-0.5/2-0.1]) cylinder(d2=6-0.5, d1=6, h=0.5/2);
        }
        
        hull() for(i=[0:1:4-1]) rotate([0,0,i*90])
        {
            translate([MHspc/2,MHspc/2,2+3.4+layH*7]) cylinder(d=6, h=1);
            translate([MHspc/2,MHspc/2,-10+25-2/2-0.1]) cylinder(d2=6-2, d1=6, h=2/2);
        }
    }
    
    translate([0,0,2+3.4]) cylinder(d=Td+tol, h=8.7*2+28.3);
    translate([0,0,2+4.1+28.3/2+8]) cylinder(d=8.5, h=28, center=true);
    translate([0,0,2+4.1+8+28.3/2]) rotate([90,0,-45/2]) hull()
    {
        cylinder(d=8, h=25);
        translate([0,0,20/2]) cube([2,9,20], center=true);
    }
    
    translate([-MHspc/3,0,25-10-5]) Bolt_cutout(size="M3", length=10, insert_extention=4, type="Flat", thread=0, layer=layH);
    translate([MHspc/3,0,25-10-5]) Bolt_cutout(size="M3", length=10, insert_extention=4, type="Flat", thread=0, layer=layH);
    
    MountingBolt_cutout(leng=25, lay=0);
}
    module Adapter_Cap() difference()
    {
        union()
        {
            for(i=[0:1:4-1]) rotate([0,0,i*90]) hull()
            {
                translate([25/2,25/2,-1]) cylinder(d=6, h=1);
                translate([25/2,25/2,-1.6-(2+3+3)]) cylinder(d1=6-0.5+3, d2=6+3, h=0.5/2);
                
                translate([0,0,-1]) cylinder(d=25+6, h=1);
            }
        }
        
        for(i=[0:1:4-1]) rotate([0,0,i*90])
        {
            translate([25/2,25/2,-1.6-(2+3+3)+3]) rotate([180,0,0]) Nut_cutout(size="M3", type="Pressfit", depth=2.5, extention=1, layer=0);
            translate([25/2,25/2,2]) rotate([180,0,0]) Bolt_cutout(size="M3", length=25, insert_extention=5, type="Flat", thread=26, layer=0);
        }
        
        translate([0,0,-9.9]) cylinder(d2=15, d1=25, h=10);
    }
    module Adapter_gasket() difference()
    {
        if(PUMPmodel == "MZB3004T04")
        {
            hull()
            {
                translate([MHspc/2,MHspc/2,2+3.4]) cylinder(d=6, h=layH*7);
                translate([MHspc/2,-MHspc/2,2+3.4]) cylinder(d=6, h=layH*7);
                translate([-MHspc/2,MHspc/2,2+3.4]) cylinder(d=6, h=layH*7);
                translate([-MHspc/2,-MHspc/2,2+3.4]) cylinder(d=6, h=layH*7);
            }
            
            // wire gasket
            hull()
            {
                translate([-21/2+6-2,-12.5,2+0.5+0.45+1/2-1.5]) rotate([90,0,0]) cylinder(d=1, h=2);
                translate([-21/2+6+6+2,-12.5,2+0.5+0.45+1/2-1.5]) rotate([90,0,0]) cylinder(d=1, h=2);
                
                translate([-21/2+6+6/2,-2/2-12.5,5]) cube([6+2*2+1,2,1], center=true);
            }
                hull()
                {
                    translate([-21/2+6+6/2,4/2-12.5-2-1/2,0.2/2+2+3.4]) cube([4,4+1,0.2], center=true);
                    translate([-21/2+6+6/2,2/2-12.5-2,0.2/2+2+0.5+tol]) cube([4,2,0.2], center=true);
                }
        }
        
        if(PUMPmodel == "MZB3004T04")
        {
            // pump cutout
            hull()
            {
                translate([19/2-1/2,19/2-1/2-1,2+3]) cylinder(d=1, h=2);
                translate([19/2-1/2,-19/2+1/2+1,2+3]) cylinder(d=1, h=2);
                translate([-19/2+1/2,19/2-1/2-1,2+3]) cylinder(d=1, h=2);
                translate([-19/2+1/2,-19/2+1/2+1,2+3]) cylinder(d=1, h=2);
            }
            
            // wire cutout
            translate([-21/2+6,-11,2+0.5+0.45+1/2]) rotate([90,0,0]) cylinder(d=1.3, h=5);
            translate([-21/2+6+6,-11,2+0.5+0.45+1/2]) rotate([90,0,0]) cylinder(d=1.3, h=5);
        }
        
        MountingBolt_cutout(leng=25, lay=layH);
    }

module TubeTool() difference()
{
    union()
    {
        translate([-5,0,22/2+6.3]) roundedBOX(dimX=40,dimY=20,dimZ=22,cornR=1);
    }
    
    // cutting cutout
    translate([-20,0,(16+5)/2+6.3-2]) hull()
    {
        cylinder(d=5+tol*5, h=16+5, center=true);
        cube([1,6,16+5], center=true);
    }
    translate([-10/2-20+6/2,0,6.3-2+5]) cube([10,25,0.5], center=true);
        // bolt plunger
    translate([-20,0,6.3-2+(16+5)]) Bolt_cutout(size="M3", length=16, insert_extention=1, type="Countersink", thread=0, layer=0);
    
    // instalation cutout
    translate([0,0,(7)/2+6.3]) hull()
    {
        cylinder(d=5+tol*5, h=7, center=true);
        cube([1,6,7], center=true);
    }
    translate([0,0,(20)/2+6.3+7]) hull()
    {
        cylinder(d=8, h=20, center=true);
        cube([1,9,20], center=true);
    }
    
    rotate([0,90,0])
    {
        translate([-(2+4.1+28.3/2+8),0,0]) cylinder(d=3.5+tol*2, h=20);
        translate([-(2+4.1+28.3/2+8),0,8]) cylinder(d=4.8+tol*2, h=20);
    }
}
module filter_CutTool() difference()
{
    hull()
    {
        translate([MHspc/2,MHspc/2,0]) cylinder(d=6, h=2, center=true);
        translate([MHspc/2,-MHspc/2,0]) cylinder(d=6, h=2, center=true);
        translate([-MHspc/2,MHspc/2,0]) cylinder(d=6, h=2, center=true);
        translate([-MHspc/2,-MHspc/2,0]) cylinder(d=6, h=2, center=true);
    }
    
    cylinder(d=16, h=2.1, center=true);
    
    for(i=[0:1:4-1]) rotate([0,0,45+i*360/4]) translate([10/2+6/2+MHspc/2,0,0]) cube([10,15,2.1], center=true);
}

// ===== ===== extra structures
module Tjoint() color([0.8,0.8,0.8,0.5]) difference()
{
    union()
    {
        rotate([0,90,0]) cylinder(d=3.5, h=28.3, center=true);
        translate([0,0,-3.5/2-1.35+3]) cylinder(d=3.5, h=17.3-3);
            translate([-28.3/2,0,0]) rotate([0,90,0]) cylinder(d1=3.5, d2=4.85, h=5.5);
            translate([0,0,(-3.5/2-1.35)+17.3]) rotate([0,180,0]) cylinder(d1=3.5, d2=4.85, h=5.5);
            translate([28.3/2,0,0]) rotate([0,-90,0]) cylinder(d1=3.5, d2=4.85, h=5.5);
        
        roundedBOX(dimX=6,dimY=6,dimZ=6,cornR=0.5);
            translate([6/2,0,0]) rotate([0,90,0]) cylinder(d1=6-0.5*2, d2=3.5, h=((6-0.5*2)-3.5)/2);
            translate([0,0,6/2]) cylinder(d1=6-0.5*2, d2=3.5, h=((6-0.5*2)-3.5)/2);
            translate([-6/2,0,0]) rotate([0,-90,0]) cylinder(d1=6-0.5*2, d2=3.5, h=((6-0.5*2)-3.5)/2);
    }
    
    translate([0,0,0]) rotate([0,90,0]) cylinder(d=2, h=29, center=true);
    translate([0,0,0]) cylinder(d=2, h=25);
}
// cutout modules
module MZB3004T04_cutout()
{
    // pump cutout
    translate([0,0,3.4/2+2]) cube([18.6+tol*3,19+tol*3,3.4], center=true);
    hull()
    {
        translate([21/2-1/2,-19/2+1/2,2+3.4-1]) cylinder(d=1+tol*3, h=1+tol*2);
        translate([21/2-1/2,19/2-1/2,2+3.4-1]) cylinder(d=1+tol*3, h=1+tol*2);
        translate([-21/2+1/2,-19/2+1/2,2+3.4-1]) cylinder(d=1+tol*3, h=1+tol*2);
        translate([-21/2+1/2,19/2-1/2,2+3.4-1]) cylinder(d=1+tol*3, h=1+tol*2);
    }
    
    // solder tab cutout
    translate([-21/2+6+6/2,-11,5/2+2+0.5]) cube([9,3,5], center=true);
    translate([-21/2+6,-11,2+0.5+0.45+1/2]) rotate([90,0,0]) hull()
    {
        cylinder(d=2, h=5);
        translate([0,2,0]) cylinder(d=2, h=5);
    }
    translate([-21/2+6+6,-11,2+0.5+0.45+1/2]) rotate([90,0,0]) hull()
    {
        cylinder(d=2, h=5);
        translate([0,2,0]) cylinder(d=2, h=5);
    }
    
    // intake hole cutout
    translate([15.5/2-1.3,0,-0.1]) cylinder(d=2, h=2.2);
    translate([-15.5/2+4.6,15.4/2-2.2,-0.1]) cylinder(d=2, h=2.2);
    translate([-15.5/2+4.6,-15.4/2+2.2,-0.1]) cylinder(d=2, h=2.2);
    
    translate([0,0,2]) cylinder(d=5+tol*3, h=4+tol*2);
    
    translate([0,0,2]) cylinder(d=5.1+tol*2, h=7.8+tol*2);
    translate([0,0,2]) cylinder(d=5+tol, h=20);
}

module MountingBolt_cutout(leng=25, lay=0)
{
    translate([MHspc/2,MHspc/2,25-10]) rotate([180,0,0]) Bolt_cutout(size="M3", length=leng, insert_extention=20, type="Flat", thread=0, layer=lay);
    translate([MHspc/2,-MHspc/2,25-10]) rotate([180,0,0]) Bolt_cutout(size="M3", length=leng, insert_extention=20, type="Flat", thread=0, layer=lay);
    translate([-MHspc/2,MHspc/2,25-10]) rotate([180,0,0]) Bolt_cutout(size="M3", length=leng, insert_extention=20, type="Flat", thread=0, layer=lay);
    translate([-MHspc/2,-MHspc/2,25-10]) rotate([180,0,0]) Bolt_cutout(size="M3", length=leng, insert_extention=20, type="Flat", thread=0, layer=lay);
}


// depriciated pump structures
module _Adapter_Base() difference()
{
    union()
    {
        if(PUMPmodel == "MZB1001T02") hull()
        {
            translate([MHspc/2,MHspc/2,0]) cylinder(d=6, h=3);
            translate([MHspc/2,-MHspc/2,0]) cylinder(d=6, h=3);
            translate([-MHspc/2,MHspc/2,0]) cylinder(d=6, h=3);
            translate([-MHspc/2,-MHspc/2,0]) cylinder(d=6, h=3);
        }
        if(PUMPmodel == "MZB3004T04") hull()
        {
            translate([MHspc/2,MHspc/2,0]) cylinder(d=6, h=2+3.4-1);
            translate([MHspc/2,-MHspc/2,0]) cylinder(d=6, h=2+3.4-1);
            translate([-MHspc/2,MHspc/2,0]) cylinder(d=6, h=2+3.4-1);
            translate([-MHspc/2,-MHspc/2,0]) cylinder(d=6, h=2+3.4-1);
        }
    }
    
    // cutout
    if(PUMPmodel == "MZB3005T06")
    {
        
    }
    if(PUMPmodel == "MZB1001T02")
    {
        // pump frame cutout
        difference()
        {
            translate([0,0,1.9/2+2]) cube([20+tol*3,20+tol*3,1.9], center=true);
            
            for(i=[0:1:3]) rotate([0,0,i*90]) translate([16.5/2,16.5/2,2-0.1]) cylinder(d=layW*5, h=1);
        }
        
        // intake hole cutout
        translate([0,0,-0.1]) cylinder(d1=9, d2=12, h=3);
        
        // electrical connection cutout
        translate([0,-MHspc/2+5/2-1,2/2+2]) cube([8,5,2], center=true);
        translate([5/2,-MHspc/2,2+0.45+1/2]) rotate([90,0,0]) cylinder(d=2, h=10);
        translate([-5/2,-MHspc/2,2+0.45+1/2]) rotate([90,0,0]) cylinder(d=2, h=10);
        
        // tube cutout
            // pump outlet pressfit
        translate([0,0,2+2.25+4/2]) rotate([90,0,0]) scale([6/5,4/5,1]) cylinder(d=5+tol*2, h=8, center=true);
            // sealed end cutout
        hull()
        {
            translate([0,-8/2,2+2.25+4/2]) rotate([90,0,0]) scale([6/5,4/5,1]) cylinder(d=5+tol*2, h=0.1);
            translate([0,-8/2-3,2+2.25+4/2]) sphere(d=5+tol*2);
        }
            // output routung
        hull()
        {
            translate([0,8/2,2+2.25+4/2]) rotate([90,0,0]) scale([6/5,4/5,1]) cylinder(d=5+tol*2, h=0.1);
            translate([0,8/2+3,2+2.25+4/2]) rotate([90,0,0]) cylinder(d=5+tol*2, h=0.1);
        }
        translate([0,8/2+3,2+2.25+4/2+Br])
        {
            rotate([0,90,0]) rotate_extrude(angle=Ba) translate([Br,0]) circle(d=5+tol*2);
            rotate([Ba,0,0]) translate([0,0,-Br]) rotate([-90,0,0]) cylinder(d1=5+tol*2, d2=10, h=3);
        }
    }
    if(PUMPmodel == "MZB3004T04") MZB3004T04_cutout();
    
    // clamping bolt cutout
    MountingBolt_cutout();
}
module _Adapter_Intermediate() difference()
{
    // base structure
    union()
    {
        if(PUMPmodel == "MZB1001T02") hull()
        {
            translate([MHspc/2,MHspc/2,3]) cylinder(d=6, h=2+2.25+4/2-3+7);
            translate([-MHspc/2,MHspc/2,3]) cylinder(d=6, h=2+2.25+4/2-3+7);
            
            translate([-MHspc/2,-MHspc/2,3]) cylinder(d=6, h=2+2.25+4/2-3);
            translate([MHspc/2,-MHspc/2,3]) cylinder(d=6, h=2+2.25+4/2-3);
        }
        
        if(PUMPmodel == "MZB3004T04") translate([0,0,2+4.1]) difference()
        {
            cylinder(d1=Td+layW*10+tol*2, d2=Td+layW*6+tol*2, h=7);
            
            translate([0,0,-0.1]) cylinder(d=Td+tol*4, h=5);
            translate([0,0,4.8]) cylinder(d=Td-tol, h=3);
            
            translate([0,-Td/2-Td/3,9/2]) cube([1,Td,10], center=true);
        }
    }
    
    if(PUMPmodel == "MZB3005T06")
    {
        
    }
    if(PUMPmodel == "MZB1001T02")
    {
        // tube split cutout
        translate([0,8/2+3,2+2.25+4/2+Br]) hull()
        {
             rotate([0,90,0]) cylinder(r=Br+tol, h=40, center=true);
             translate([0,-(8/2+3)-MHspc/2-5,0]) rotate([0,90,0]) cylinder(r=Br+tol, h=40, center=true);
             rotate([Ba,0,0]) translate([0,Br,0]) rotate([0,90,0]) cylinder(r=Br+tol, h=40, center=true);
        }
                
        // electrical connection cutout
        translate([0,-MHspc/2+5/2-1,2/2+2]) hull()
        {
            cube([8,5,2], center=true);
                cube([8,7,0.1], center=true);
        }
        translate([5/2,-MHspc/2,2+0.45+1/2]) rotate([90,0,0]) cylinder(d=2, h=10);
        translate([-5/2,-MHspc/2,2+0.45+1/2]) rotate([90,0,0]) cylinder(d=2, h=10);
        
        // pump cutout
        translate([0,0,1.9/2+2])
        hull()
        {
            cube([20+tol*3,20+tol*3,1.9], center=true);
                translate([0,-1,0]) cube([20+tol*3,20+tol*3+1,0.1], center=true);
        }
            translate([0,0,2]) cylinder(d=4+tol*4, h=3);
        
        // tube cutout
            // pump outlet pressfit
        translate([0,0,2+2.25+4/2]) rotate([90,0,0]) scale([6/5,4/5,1]) cylinder(d=5+tol*2, h=8, center=true);
            // sealed end cutout
        hull()
        {
            translate([0,-8/2,2+2.25+4/2]) rotate([90,0,0]) scale([6/5,4/5,1]) cylinder(d=5+tol*2, h=0.1);
            translate([0,-8/2-3,2+2.25+4/2]) sphere(d=5+tol*2);
        }
            // output routung
                Br=6;   // tube bend radius
                Ba=80;  // tube bend angle
        hull()
        {
            translate([0,8/2,2+2.25+4/2]) rotate([90,0,0]) scale([6/5,4/5,1]) cylinder(d=5+tol*2, h=0.1);
            translate([0,8/2+3,2+2.25+4/2]) rotate([90,0,0]) cylinder(d=5+tol*2, h=0.1);
        }
        translate([0,8/2+3,2+2.25+4/2+Br])
        {
            rotate([0,90,0]) rotate_extrude(angle=Ba) translate([Br,0]) circle(d=5+tol*2);
            rotate([Ba,0,0]) translate([0,0,-Br]) rotate([-90,0,0]) cylinder(d1=5+tol*2, d2=12, h=6);
        }
    }
    if(PUMPmodel == "MZB3004T04")
    {
        
    }
    
    // clamping bolt cutout
    MountingBolt_cutout();
}
module _Adapter_TopCover() difference()
{
    // base structure
    union()
    {
        if(PUMPmodel == "MZB1001T02") intersection()
        {
            union()
            {
                hull()
                {
                    translate([MHspc/2,MHspc/2,2+2.25+4/2+7+tol]) rotate_extrude() translate([6/2-3/2,0]) circle(d=3);
                    translate([-MHspc/2,MHspc/2,2+2.25+4/2+7+tol]) rotate_extrude() translate([6/2-3/2,0]) circle(d=3);
                    translate([MHspc/2,MHspc/2,3]) cylinder(d=6, h=2+2.25+4/2-3+7);
                    translate([-MHspc/2,MHspc/2,3]) cylinder(d=6, h=2+2.25+4/2-3+7);
                    
                    translate([-MHspc/2,-MHspc/2,2+2.25+4/2+7+tol]) rotate_extrude() translate([6/2-3/2,0]) circle(d=3);
                    translate([MHspc/2,-MHspc/2,2+2.25+4/2+7+tol]) rotate_extrude() translate([6/2-3/2,0]) circle(d=3);
                    translate([-MHspc/2,-MHspc/2,3]) cylinder(d=6, h=2+2.25+4/2-3);
                    translate([MHspc/2,-MHspc/2,3]) cylinder(d=6, h=2+2.25+4/2-3);
                }
                
                translate([MHspc/2,MHspc/2,2+2.25+4/2+7+tol]) cylinder(d=6, h=3/2);
                translate([-MHspc/2,MHspc/2,2+2.25+4/2+7+tol]) cylinder(d=6, h=3/2);
                translate([-MHspc/2,-MHspc/2,2+2.25+4/2+7+tol]) cylinder(d=6, h=3/2);
                translate([MHspc/2,-MHspc/2,2+2.25+4/2+7+tol]) cylinder(d=6, h=3/2);
            }
            
            union()
            {
                translate([0,8/2+3,2+2.25+4/2+Br]) hull() // tube split cutout
                {
                     rotate([0,90,0]) cylinder(r=Br-tol, h=40, center=true);
                     translate([0,-(8/2+3)-MHspc/2-5,0]) rotate([0,90,0]) cylinder(r=Br-tol, h=40, center=true);
                     rotate([Ba,0,0]) translate([0,Br,0]) rotate([0,90,0]) cylinder(r=Br-tol, h=40, center=true);
                }
                
                translate([0,0,5/2+(2+2.25+4/2+7+tol)]) cube([40,40,5], center=true);
            }
        }
        
        if(PUMPmodel == "MZB3004T04") translate([0,0,2+3.4-1+tol])
        {
            hull()
            {
                translate([MHspc/2,MHspc/2,0]) rotate_extrude() translate([6/2-3/2,10-3/2]) circle(d=3);
                translate([-MHspc/2,MHspc/2,0]) rotate_extrude() translate([6/2-3/2,10-3/2]) circle(d=3);
                translate([-MHspc/2,-MHspc/2,0]) rotate_extrude() translate([6/2-3/2,10-3/2]) circle(d=3);
                translate([MHspc/2,-MHspc/2,0]) rotate_extrude() translate([6/2-3/2,10-3/2]) circle(d=3);
                
                translate([MHspc/2,MHspc/2,0]) cylinder(d=6, h=1);
                translate([-MHspc/2,MHspc/2,0]) cylinder(d=6, h=1);
                translate([-MHspc/2,-MHspc/2,0]) cylinder(d=6, h=1);
                translate([MHspc/2,-MHspc/2,0]) cylinder(d=6, h=1);
            }
            translate([MHspc/2,MHspc/2,0]) cylinder(d=6, h=10);
            translate([-MHspc/2,MHspc/2,0]) cylinder(d=6, h=10);
            translate([-MHspc/2,-MHspc/2,0]) cylinder(d=6, h=10);
            translate([MHspc/2,-MHspc/2,0]) cylinder(d=6, h=10);
        }
    }
    
    // cutout
    if(PUMPmodel == "MZB3005T06")
    {
        
    }
    if(PUMPmodel == "MZB1001T02")
    {
        // pump cutout
        translate([0,0,1.9/2+2]) cube([20+tol*3,20+tol*3,1.9], center=true);
            translate([0,0,2]) cylinder(d=4+tol*4, h=3);
        
        // tube cutout
            // pump outlet pressfit
        translate([0,0,2+2.25+4/2]) rotate([90,0,0]) scale([6/5,4/5,1]) cylinder(d=5+tol*2, h=8, center=true);
            // sealed end cutout
        hull()
        {
            translate([0,-8/2,2+2.25+4/2]) rotate([90,0,0]) scale([6/5,4/5,1]) cylinder(d=5+tol*2, h=0.1);
            translate([0,-8/2-3,2+2.25+4/2]) sphere(d=5+tol*2);
        }
            // output routung
                Br=6;   // tube bend radius
                Ba=80;  // tube bend angle
        hull()
        {
            translate([0,8/2,2+2.25+4/2]) rotate([90,0,0]) scale([6/5,4/5,1]) cylinder(d=5+tol*2, h=0.1);
            translate([0,8/2+3,2+2.25+4/2]) rotate([90,0,0]) cylinder(d=5+tol*2, h=0.1);
        }
        translate([0,8/2+3,2+2.25+4/2+Br])
        {
            rotate([0,90,0]) rotate_extrude(angle=Ba) translate([Br,0]) circle(d=5+tol*2);
            rotate([Ba,0,0]) translate([0,0,-Br]) rotate([-90,0,0]) cylinder(d1=5+tol*2, d2=12, h=6);
        }
        
        // text
        translate([0,7,2+3.4-1+tol+10.5-1/2]) linear_extrude(1) text("MZB1001T02", size=3.4, font="Liberation Sans:style=Bold", halign="center", valign="center");
    }
    if(PUMPmodel == "MZB3004T04")
    {
        // clamping cone cutout
        translate([0,0,2+3.41]) cylinder(d=Td+tol+layW*10, h=(4.1+0.1)-3.4);
        translate([0,0,2+4.1+0.1]) cylinder(d1=Td+tol+layW*10, d2=Td+tol+layW*6, h=7);
        
        MZB3004T04_cutout();
        
        // text
        //translate([0,7,2+3.4-1+tol+10-1/2]) linear_extrude(1) text("MZB3004T04", size=3.4, font="Liberation Sans:style=Bold", halign="center", valign="center");
    }
    
    // clamping bolt cutout
    MountingBolt_cutout();
}