//$fn=60;
//tol=0.1;

//Bolt_cutout(size="M3", length=16, insert_extention=5, type="Flat", thread=5, layer=0.2);
//Bolt_cutout(size="M2.5", length=16, insert_extention=5, type="HEX", thread=5, layer=0.2);
//Nut_cutout(size="M3", type="Pressfit", depth=3, extention=7, layer=0.2);
//Bolt(size="M3", length=15, Headtype="Flat", driverType="HEX", driverSize=2.5);
//Nut(size="M3", "Security");

//AluProfile_SlotClip(slotW=10, slotTH=5.7, stemEXT=1, headTH=2.5, headW=20);

    // ===== ===== ===== BOLTS ===== ===== =====
module Bolt(size="M3", length=15, Headtype="Flat", driverType="HEX", driverSize=2.5)
{
    if(size == "M2.5")
    {
        if(Headtype=="Flat") Flat(5.3,2.5,2.5,length,0,false);
        if(Headtype=="HEX") HEXbolt(5,2.5,2.5,length,0,false);
    }
    if(size == "M3")
    {
        if(Headtype=="Countersink") Countersink(5.3,0.3,3,length,driverType,driverSize);
        if(Headtype=="Flat") Flat(5.3,2.5,3,length,driverType,driverSize);
        if(Headtype=="DIN7984") Flat(5.5,2,3,length,"HEX",2);
    }
    if(size == "M4")
    {
        if(Headtype=="DIN6912") Flat(7,2.8,4,length,"HEX",3);
        if(Headtype=="DIN7984") Flat(7,2.8,4,length,"HEX",2.5);
    }
    if(size == "M5")
    {
        if(Headtype=="Flat") Flat(8.4,3.4,5,length,0);
        if(Headtype=="DIN6912") Flat(8.5,3.5,5,length,"HEX",4);
        if(Headtype=="DIN7984") Flat(8.5,3.5,5,length,"HEX",3);
    }
    if(size == "M6")
    {
        if(Headtype=="DIN6912") Flat(10,4,6,length,"HEX",5);
        if(Headtype=="DIN7984") Flat(10,4,6,length,"HEX",4);
    }
    if(size == "M8")
    {
        if(Headtype=="DIN6912") Flat(13,5,8,length,"HEX",6);
        if(Headtype=="DIN7984") Flat(13,5,8,length,"HEX",5);
    }
    if(size == "M10")
    {
        if(Headtype=="DIN6912") Flat(16,6.5,10,length,"HEX",8);
        if(Headtype=="DIN7984") Flat(16,6,10,length,"HEX",7);
    }
}

module Bolt_cutout(size="M3", length=16, insert_extention=5, type="Countersink", thread=10, layer=0.2)
{
    if(size == "M2.5")
    {
        if(type=="Countersink")
        {
            Countersink_cutout(6,0.7,insert_extention,2.2+tol,length);
            Countersink_cutout(6,0.7,insert_extention,2.5+tol*2,length-thread);
        }
        if(type=="Flat")
        {
            Flat_cutout(6,insert_extention,2.2+tol,length,layer);
            Flat_cutout(6,insert_extention,2.5+tol*2,length-thread,layer);
        }
        if(type=="sFlat")
        {
            Flat_cutout(5.8,insert_extention,2.2+tol,length,layer,true);
            Flat_cutout(5.8,insert_extention,2.5+tol*2,length-thread,0,true);
        }
        if(type=="HEX")
        {
            HEXbolt_cutout(5+tol*3,insert_extention,2.2+tol,length,layer,false,true);
            HEXbolt_cutout(5+tol*3,insert_extention,2.5+tol*2,length-thread,layer,false,true);
        }
    }
    if(size == "M3")
    {
        if(type=="Countersink")
        {
            Countersink_cutout(6,0.7,insert_extention,2.4+tol,length);
            Countersink_cutout(6,0.7,insert_extention,3+tol*2,length-thread);
        }
        if(type=="sCountersink")
        {
            Countersink_cutout(6,0.7,insert_extention,2.4+tol,length);
            sCountersink_cutout(6,0.7,insert_extention,3+tol*2,length-thread);
        }
        if(type=="Flat")
        {
            Flat_cutout(5.8,insert_extention,2.4+tol*2,length,layer);
            Flat_cutout(5.8,insert_extention,3+tol*2,length-thread,layer);
        }
        if(type=="sFlat")
        {
            Flat_cutout(5.8,insert_extention,2.4+tol,length,layer,true);
            Flat_cutout(5.8,insert_extention,3+tol*2,length-thread,0,true);
        }
    }
    if(size == "M4")
    {
        if(type=="Countersink")
        {
            Countersink_cutout(8.5,1,insert_extention,3.2+tol,length);
            Countersink_cutout(8.5,1,insert_extention,4+tol*2,length-thread);
        }
        if(type=="sCountersink")
        {
            Countersink_cutout(8.5,1,insert_extention,3.2+tol,length);
            sCountersink_cutout(8.5,1,insert_extention,4+tol*2,length-thread);
        }
        if(type=="Flat")
        {
            Flat_cutout(8.5,insert_extention,3.2-tol,length,layer);
            Flat_cutout(8.5,insert_extention,4+tol*2,length-thread,layer);
        }
        if(type=="sFlat")
        {
            Flat_cutout(8.5,insert_extention,3.2-tol,length,layer,true);
            Flat_cutout(8.5,insert_extention,4+tol*2,length-thread,layer,true);
        }
    }
    if(size == "M5")
    {
        if(type=="Countersink")
        {
            Countersink_cutout(10.5,1,insert_extention,4.1+tol,length);
            Countersink_cutout(10.5,1,insert_extention,5+tol*2,length-thread);
        }
        if(type=="Flat")
        {
            Flat_cutout(10.5,insert_extention,4.1+tol,length,layer);
            Flat_cutout(10.5,insert_extention,5+tol*2,length-thread,layer);
        }
    }
    if(size == "M6")
    {
        if(type=="Countersink")
        {
            Countersink_cutout(11.5,1,insert_extention,5+tol,length);
            Countersink_cutout(11.5,1,insert_extention,6+tol*2,length-thread);
        }
        if(type=="Flat")        // DIN6912, DIN7984
        {
            Flat_cutout(10+tol*5,insert_extention,5+tol,length,layer);
            Flat_cutout(10+tol*5,insert_extention,6+tol*2,length-thread,layer);
        }
         if(type=="sFlat")      // DIN6912, DIN7984
         {
            Flat_cutout(10+tol*5,insert_extention,5+tol,length,layer,true);
            Flat_cutout(10+tol*5,insert_extention,6+tol*2,length-thread,layer,true);
        }
    }
    if(size == "M8")
    {
        if(type=="Flat")        // DIN6912, DIN7984
        {
            Flat_cutout(13+tol*5,insert_extention,6.7+tol,length,layer);
            Flat_cutout(13+tol*5,insert_extention,8+tol*2,length-thread,layer);
        }
        if(type=="sFlat")        // DIN6912, DIN7984
        {
            Flat_cutout(13+tol*5,insert_extention,6.7+tol,length,layer,true);
            Flat_cutout(13+tol*5,insert_extention,8+tol*2,length-thread,layer,true);
        }
    }
    if(size == "M10")
    {
        if(type=="Flat")        // DIN6912, DIN7984
        {
            Flat_cutout(16+tol*5,insert_extention,8.5+tol,length,layer);
            Flat_cutout(16+tol*5,insert_extention,10+tol*2,length-thread,layer);
         }
    }
}
    module Countersink(headD,headH,boltD,length,driverTYPE,driverSIZE) difference()
    {
        color([0.7,0.7,0.7])
        {
            cylinder(d=headD, h=headH);
            translate([0,0,headH-0.01]) cylinder(d1=headD, d2=boltD, h=(headD-boltD)/2);
            
            hull()
            {
                cylinder(d=boltD, h=1);
                translate([0,0,length-boltD/7]) cylinder(d1=boltD, d2=boltD*6/7, h=boltD/7);
            }
        }
        
        color([0.5,0.5,0.5])
        {
            if(driverTYPE == "HEX") translate([0,0,-0.01]) linear_extrude(driverSIZE/2) hexagon(driverSIZE);
        }
    }
    module Countersink_cutout(headD,headH,headEXT,boltD,length,lay)
    {
        translate([0,0,-headEXT]) cylinder(d=headD, h=headH+headEXT);
        translate([0,0,headH-0.01]) cylinder(d1=headD, d2=boltD, h=(headD-boltD)/2);
        hull()
        {
            cylinder(d=boltD, h=1);
            translate([0,0,length]) cylinder(d1=boltD, d2=0, h=boltD/2);
        }
    }
    module sCountersink_cutout(headD,headH,headEXT,boltD,length,lay)
    {
        hull()
        {
            translate([0,0,-headEXT]) cylinder(d=headD, h=headH+headEXT);
            translate([headD/2,0,-(headH+headEXT)/2+headH]) cube([headD/7,headD/5,headH+headEXT], center=true);
        }
            
        hull()
        {
            translate([0,0,headH-0.01]) cylinder(d1=headD, d2=boltD, h=(headD-boltD)/2);
            
            translate([headD/2,0,-1/2+headH]) cube([headD/7,headD/5,1], center=true);
            translate([boltD/2,0,-1/2+headH+(headD-boltD)/2]) cube([boltD/7,boltD/5,1], center=true);
        }
        hull()
        {
            cylinder(d=boltD, h=1);
            translate([0,0,length]) cylinder(d1=boltD, d2=0, h=boltD/2);
            
            translate([boltD/2,0,length/2]) cube([boltD/7,boltD/5,length], center=true);
        }
    }
    module Flat(headD,headH,boltD,length,driverTYPE,driverSIZE) difference()
    {
        color([0.7,0.7,0.7])
        {
            hull()
            {
                rotate_extrude() translate([headD/2-headD/20,-headD/20]) circle(d=headD/10);
                rotate_extrude() translate([headD/2-headD/20,-headH+headD/20]) circle(d=headD/10);
            }
            
            hull()
            {
                cylinder(d=boltD, h=1);
                translate([0,0,length-boltD/7]) cylinder(d1=boltD, d2=boltD*6/7, h=boltD/7);
            }
        }
        
        color([0.5,0.5,0.5])
        {
            if(driverTYPE == "HEX") translate([0,0,-headH-0.01]) linear_extrude(driverSIZE/2) hexagon(driverSIZE);
        }
    }
    module Flat_cutout(headD,headEXT,boltD,length,lay,side=false)
    {
        if(side)
        {
            hull()
            {
                translate([0,0,-headEXT+0.1]) cylinder(d=headD, h=headEXT);
                translate([headD/2,0,-headEXT/2+0.1]) cube([0.7,headD/5,headEXT], center=true);
            }
            hull()
            {
                cylinder(d=boltD, h=length);
                translate([boltD/2,0,length/2]) cube([0.7/2,boltD/5,length], center=true);
            }
        }
        else
        {
            hull()
            {
                cylinder(d=boltD, h=1);
                translate([0,0,length]) cylinder(d1=boltD, d2=0, h=boltD/2);
            }
            translate([0,0,-headEXT+0.1]) cylinder(d=headD, h=headEXT);
        }
        
        if(!$preview) intersection()
        {
            cylinder(d=headD, h=lay*1.5*3);
            
            union()
            {
                translate([0,0,lay*2.5*1.5]) intersection()
                {
                    intersection()
                    {
                        translate([0,0,0]) cube([boltD,headD,lay*1.5+0.01], center=true);
                        
                        translate([0,0,0]) rotate([0,0,120]) cube([boltD,headD,lay*1.5+0.01], center=true);
                    }
                    
                    translate([0,0,0]) rotate([0,0,120*2]) cube([boltD,headD,lay*1.5+0.01], center=true);
                }
                translate([0,0,lay*2.5/2]) intersection()
                {
                    translate([0,0,lay]) rotate([0,0,120]) cube([boltD,headD,lay*1.5+0.01], center=true);
                    
                    translate([0,0,lay]) rotate([0,0,120*2]) cube([boltD,headD,lay*1.5+0.01], center=true);
                }
                translate([0,0,lay*1.5/2]) rotate([0,0,120*2]) cube([boltD,headD,lay*1.5+0.01], center=true);
            }
        }
    }
    module HEXbolt(headW,headTH,boltD,length)
    {
        cylinder(d=boltD, h=length);
        translate([0,0,-headTH]) linear_extrude(headTH) hexagon(headW);
    }
    module HEXbolt_cutout(headW,headEXT,boltD,length,lay,side=false,pressfit=false)
    {
        if(side)
        {
            
        }
        else
        {
            cylinder(d=boltD, h=length);
            if(pressfit) translate([0,0,-headEXT])  difference()
            {
                linear_extrude(headEXT+0.01) hexagon(headW);
                
                for(i=[0:1:5]) rotate([0,0,i*360/6])
                {
                    translate([headW/2*1.1,0,headW*0.2]) cylinder(d=headW*0.2, h=headEXT*0.8+lay*3);
                    translate([headW/2*1.1,0,0]) cylinder(d2=headW*0.2, d1=0, h=headW*0.2);
                }
            }
                else translate([0,0,-headEXT]) linear_extrude(headEXT) hexagon(headW);
        }
        
        if(!$preview) intersection()
        {
            linear_extrude(lay*3*1.5) hexagon(headW);
            
            rotate([0,0,30])
            {
                translate([0,0,lay*2.5*1.5]) intersection()
                {
                    intersection()
                    {
                        translate([0,0,0]) cube([boltD,headW,lay*1.5+0.01], center=true);
                        
                        translate([0,0,0]) rotate([0,0,120]) cube([boltD,headW,lay*1.5+0.01], center=true);
                    }
                    
                    translate([0,0,0]) rotate([0,0,120*2]) cube([boltD,headW,lay*1.5+0.01], center=true);
                }
                translate([0,0,lay*2.5/2]) intersection()
                {
                    translate([0,0,lay]) rotate([0,0,120]) cube([boltD,headW,lay*1.5+0.01], center=true);
                    
                    translate([0,0,lay]) rotate([0,0,120*2]) cube([boltD,headW,lay*1.5+0.01], center=true);
                }
                translate([0,0,lay*1.5/2]) rotate([0,0,120*2]) cube([boltD,headW,lay*1.5+0.01], center=true);
            }
        }
    }

module Bolt_camera() color([0.7,0.7,0.7])
{
    cylinder(d=12, h=3.2);
    union()
    {
        translate([12/2,0,3.2/2]) rotate([0,90,0]) cylinder(d=3.2, h=2);
        translate([-12/2,0,3.2/2]) rotate([0,-90,0]) cylinder(d=3.2, h=2);
        scale([1,((11.5-8.3)+12/2)/(12/2+2),1]) rotate_extrude(angle=180) translate([12/2+2/2,3.2/2]) square([2,3.22], center=true);
    }
    translate([0,0,3.2]) cylinder(d=25.4/4, h=10);
}

    // ===== ===== ===== NUTS ===== ===== =====
module Nut(size="M3", type)
{
    if(size == "M2")
    {
        if(type == "Security")
        {
            NUT(4,2,2);
            securityPocket(4,2,3,2);
        }
        else NUT(4,1.6,2);  // DIN934
    }
    if(size == "M2.5")
    {
        if(type == "Security")
        {
            NUT(5,2.3,2.5);
            securityPocket(5,2.3,3.8,2.5);
        }
        else NUT(5,2,2.5);  // DIN934
    }
    if(size == "M3")
    {
        if(type == "Security")
        {
            NUT(5.5,2.4,3);
            securityPocket(5.5,2.4,4,3);
        }
        else if(type == "Square") SquareNut(5.5,1.8,3); // DIN562
        else NUT(5.5,2.4,3);    // DIN934
    }
    if(size == "M4")
    {
        if(type == "Security")
        {
            NUT(7,2.9,4);
            securityPocket(7,2.9,5,4);
        }
        else if(type == "Square") SquareNut(7,2.2,4);   // DIN562
        else if(type == "Square+") DIN557(7,3,4);
        else NUT(7,3.2,4);  // DIN934
    }
    if(size == "M5")
    {
        if(type == "Security")
        {
            NUT(8,3.2,5);
            securityPocket(8,3.2,5,5);
        }
        else if(type == "Square") SquareNut(8,2.7,5);   // DIN562
        else if(type == "Square+") DIN557(8,4,5);
        else NUT(8,4,5);    // DIN934
    }
    if(size == "M6")
    {
        if(type == "Security")
        {
            NUT(10,4.7,6);
            securityPocket(10,4.7,6,6);
        }
        else if(type == "Square") SquareNut(10,3.2,6);  // DIN562
        else if(type == "Square+") DIN557(10,5,6);
        else NUT(10,5,6);   // DIN934
    }
    if(size == "M8")
    {
        if(type == "Square") SquareNut(13,4,8); // DIN562
        else if(type == "Square+") DIN557(13,6.5,8);
        NUT(13,6.5,8);   // DIN934
    }
    if(size == "M10")
    {
        if(type == "Square") SquareNut(17,5,10);    // DIN562
        else if(type == "Square+") DIN557(17,8,10);
        NUT(17,8,10);   // DIN934
    }
}
module Nut_cutout(size="M3", type="Pressfit", depth=3, extention=7, layer=0.2)
{
    if(size == "M2.5")
    {
        if(type=="Pressfit") nut_PressfitCutout(5+tol*2,2.5+tol*3,depth,extention,layer);
        else if(type=="Square") nut_SquareCutout(5+tol*2,2.5+tol*3,1.7+tol*2,extention,layer);
            else nut_Cutout(5+tol*2,2.5+tol*3,depth,extention,layer);
    }
    if(size == "M3")
    {
        if(type=="Pressfit") nut_PressfitCutout(5.5+tol*2,3+tol*3,depth,extention,layer);
        else if(type=="Square") nut_SquareCutout(5.5+tol*2,3+tol*3,1.7+tol*2,extention,layer);
        else nut_Cutout(5.5+tol*2,3+tol*3,depth,extention,layer);
    }
    if(size == "M4")
    {
        if(type=="Pressfit") nut_PressfitCutout(7+tol*2,4+tol*3,depth,extention,layer);
        else nut_Cutout(7+tol*2,4+tol*3,depth,extention,layer);
    }
    if(size == "M5")
    {
        if(type=="Pressfit") nut_PressfitCutout(8+tol*2,5+tol*3,depth,extention,layer);
        else nut_Cutout(8+tol*2,5+tol*3,depth,extention,layer);
    }
    if(size == "M6")
    {
        if(type=="Pressfit") nut_PressfitCutout(10+tol*2,6+tol*3,depth,extention,layer);
        else nut_Cutout(10+tol*2,6+tol*3,depth,extention,layer);
    }
    if(size == "M8")
    {
        if(type=="Pressfit") nut_PressfitCutout(13+tol*2,8+tol*3,depth,extention,layer);
        else nut_Cutout(13+tol*2,8+tol*3,depth,extention,layer);
    }
    if(size == "M10")
    {
        if(type=="Pressfit") nut_PressfitCutout(17+tol*2,10+tol*3,depth,extention,layer);
        else nut_Cutout(17+tol*2,10+tol*3,depth,extention,layer);
    }
}
module Spacer_HEX(size="M3", length=10, thread=true)
{
	if(size=="M3")
	{
		if(thread) NUT(5.5,length,2.5);
		else NUT(5.5,length,3.2);
	}
}
    module NUT(wrenchW,height,boltD)
    {
        color([0.7,0.7,0.7]) difference()
        {
            intersection()      // nut
            {
                linear_extrude(height) minkowski()  // base rounded structure
                {
                    hexagon(wrenchW-wrenchW/6);
                    circle(d=wrenchW/6);
                }
                
                union()                             // top & bottom chamfer
                {
                    cylinder(d1=wrenchW, d2=wrenchW*1.13, h=(wrenchW*0.13)/2);
                    translate([0,0,(wrenchW*0.13)/2]) cylinder(d=wrenchW*1.13, h=height-(wrenchW*0.13));
                    translate([0,0,height-(wrenchW*0.13)/2]) cylinder(d1=wrenchW*1.13, d2=wrenchW, h=(wrenchW*0.13)/2);
                }
            }
            
            translate([0,0,-0.1]) cylinder(d=boltD, h=height+0.2);
        }
    }
    module SquareNut(wrenchW,height,boltD) difference()
    {
        color([0.7,0.7,0.7]) translate([0,0,height/2]) cube([wrenchW,wrenchW,height], center=true);
        
        color([0.5,0.5,0.5]) translate([0,0,-0.1]) cylinder(d=boltD, h=height*1.1);
    }
    module DIN557(wrenchW,height,boltD) difference()
    {
        color([0.7,0.7,0.7]) hull()
        {
            translate([0,0,height*0.8/2]) cube([wrenchW,wrenchW,height*0.85], center=true);
            translate([0,0,height*0.1/2]) cylinder(d=wrenchW, h=height*0.95);
        }
        
        color([0.5,0.5,0.5]) translate([0,0,-0.1]) cylinder(d=boltD, h=height*1.1);
    }
        module securityPocket(wrenchW,height,Sheight,boltD)
        {
            color([0.7,0.7,0.7]) difference()
            {
                hull()              // security pocket
                {
                    translate([0,0,Sheight-wrenchW/7]) rotate_extrude() translate([wrenchW/2-wrenchW/7,0]) circle(r=wrenchW/7);
                    cylinder(d=wrenchW, h=1);
                }
                
                translate([0,0,-0.1]) cylinder(d=boltD, h=Sheight+0.2); // bolt hole
                
                translate([0,0,height]) cylinder(d=wrenchW-1.5, h=(Sheight-height)-0.5);
            }
            
            color([0.1,0.1,0.9]) translate([0,0,height]) difference()   // security plastic
            {
                cylinder(d=wrenchW-1.5, h=(Sheight-height)-0.5);
                translate([0,0,-0.1]) cylinder(d=boltD*0.9, h=(Sheight-height)-0.3);
            }
        }
        module nut_Cutout(wdt,hol,hgt,ext,lay)
        {
            translate([0,0,lay*3*1.5]) hull()
            {
                linear_extrude(hgt+ext) hexagon(wdt);
                
                if(ext > 0) translate([0,0,hgt+ext+wdt*0.5]) sphere(d=0.2);
            }
            
            if(!$preview) intersection()
            {
                linear_extrude(lay*3*1.5) hexagon(wdt);
                
                rotate([0,0,30])
                {
                    translate([0,0,-lay*1.5/6]) intersection()
                    {
                        intersection()
                        {
                            translate([0,0,lay]) cube([hol,wdt,lay*1.5], center=true);
                            
                            translate([0,0,lay]) rotate([0,0,120]) cube([hol,wdt,lay*1.5], center=true);
                        }
                        
                        translate([0,0,lay]) rotate([0,0,120*2]) cube([hol,wdt,lay*1.5], center=true);
                    }
                    translate([0,0,lay*2.5/2]) intersection()
                    {
                        translate([0,0,lay]) rotate([0,0,120]) cube([hol,wdt,lay*1.5], center=true);
                        
                        translate([0,0,lay]) rotate([0,0,120*2]) cube([hol,wdt,lay*1.5], center=true);
                    }
                    translate([0,0,lay*2.5*1.5]) rotate([0,0,120*2]) cube([hol,wdt,lay*1.5], center=true);
                }
            }
            else linear_extrude(lay*3*1.5) hexagon(wdt*0.8);
        }
        module nut_PressfitCutout(wdt,hol,hgt,ext,lay) difference()
        {
            nut_Cutout(wdt,hol,hgt,ext,lay);
            
            for(i=[0:1:5]) rotate([0,0,i*360/6])
            {
                translate([wdt/2*1.1,0,0]) cylinder(d=wdt*0.2, h=hgt*0.8+lay*3);
                translate([wdt/2*1.1,0,hgt*0.8+lay*3]) cylinder(d1=wdt*0.2, d2=0, h=wdt*0.2);
            }
        }
		module nut_SquareCutout(wdt,hol,hgt,ext,lay)
		{
			translate([-(wdt+ext+0.5)/2+wdt/2+0.5,0,(hgt+lay)/2]) cube([wdt+ext+0.5,wdt,hgt+lay], center=true);
			
			if(!$preview)
            {
                translate([0,0,-(lay*1.5)/2]) cube([hol,wdt,lay*1.5], center=true);
                translate([0,0,-(lay*1.5*2)/2]) cube([hol,hol,lay*1.5*2], center=true);
            }
            else translate([0,0,-(lay*1.5*2)/2]) cube([hol,hol,lay*1.5*2], center=true);
		}
module hexagon(W) for(i=[0:1:5]) rotate([0,0,i*360/3]) square([W,W/sqrt(3)], center=true);
    

    // ===== ===== ===== Threaded brass inserts ===== ===== =====
        /*
        M2   : D=3.2mm ; Dh=2.8mm
        M2.5 : D=3.5mm ; Dh=3.1mm
        M3   : D=5.0mm ; Dh=4.2mm
        M4   : D=6.0mm ; Dh=5.3mm
        M5   : D=7.0mm ; Dh=6.1mm
        M6   : D=8.0mm ; Dh=7.1mm
        */
module ThreadedInsert(size="M3", length=6, insert_extention=1)
{
    if(size == "M2") hull()
    {
        translate([0,0,-insert_extention]) cylinder(d=2.8+tol*2, h=0.1+insert_extention);
        translate([0,0,length]) cylinder(d1=2.8+tol*2, d2=0, h=2.8/2);
    }
    if(size == "M2.5") hull()
    {
        translate([0,0,-insert_extention]) cylinder(d=3.1+tol*2, h=0.1+insert_extention);
        translate([0,0,length]) cylinder(d1=3.1+tol*2, d2=0, h=3.1/2);
    }
    if(size == "M3") hull()
    {
        translate([0,0,-insert_extention]) cylinder(d=4.2+tol*2, h=0.1+insert_extention);
        translate([0,0,length]) cylinder(d1=4.2+tol*2, d2=0, h=4.2/2);
    }
    if(size == "M4") hull()
    {
        translate([0,0,-insert_extention]) cylinder(d=5.3+tol*2, h=0.1+insert_extention);
        translate([0,0,length]) cylinder(d1=5.3+tol*2, d2=0, h=5.3/2);
    }
    if(size == "M5") hull()
    {
        translate([0,0,-insert_extention]) cylinder(d=6.1+tol*2, h=0.1+insert_extention);
        translate([0,0,length]) cylinder(d1=6.1+tol*2, d2=0, h=6.1/2);
    }
    if(size == "M6") hull()
    {
        translate([0,0,-insert_extention]) cylinder(d=7.1+tol*2, h=0.1+insert_extention);
        translate([0,0,length]) cylinder(d1=7.1+tol*2, d2=0, h=7.1/2);
    }
    if(size == "Prusa_M6")
    {
        translate([0,0,0]) cylinder(d=7.3+tol*2, h=insert_extention);
        translate([0,0,3]) cylinder(d=7.3+tol*2, h=7.3/2);
    }
}

    // ===== ===== ===== Drywall screws ===== ===== =====
/*
https://www.drywallscrews.cn/standards.htm
*/
module ScrewDrywall(size="3.9", length=65, thread=4.2, boost=0)
{
    if(size == "3.9")
    {
        translate([0,0,-boost*20]) cylinder(d=8.2+boost, h=0.8+boost*20);
        difference()
        {
            translate([0,0,0.8]) cylinder(d1=8.2+boost, d2=2.5+boost, h=7);
            
            rotate_extrude() translate([10+2.5/2+boost,7+0.8]) circle(r=10+boost/2);
        }
        cylinder(d=thread+boost, h=length-2.8*2);
        translate([0,0,length-2.8*2]) cylinder(d1=thread+boost, d2=0.2, h=2.8*2);
    }
}

    // ===== ===== ===== Extruded Profile Slot Clip ===== ===== =====
module AluProfile_SlotClip(slotW=10, slotTH=5.7, stemEXT=1, headTH=2.5, headW=20)
{
    // Stem
    hull()
    {
        translate([-(slotW-tol)/2,0,-stemEXT]) cylinder(d=slotW-tol, h=slotTH+stemEXT+1);
        
        translate([-1/2,(slotW-tol)/2-1/2,-stemEXT]) cylinder(d=1, h=slotTH+stemEXT+1);
        translate([-(slotW-tol)+1/2,-(slotW-tol)/2+1/2,-stemEXT]) cylinder(d=1, h=slotTH+stemEXT+1);
    }
    // Head
    hull()
    {
        translate([-1/2,headW/2-tol-1/2,slotTH+1/2+tol]) sphere(d=1);
        translate([-(slotW-tol)/2,headW/2-tol-(slotW-tol)/2,slotTH+1/2+tol]) rotate_extrude() translate([(slotW-tol)/2-1/2,0]) circle(d=1);
        translate([-(slotW-tol)/2,-headW/2+tol+(slotW-tol)/2,slotTH+1/2+tol]) rotate_extrude() translate([(slotW-tol)/2-1/2,0+tol]) circle(d=1);
        translate([-(slotW-tol)+1/2,-headW/2+tol+1/2,slotTH+1/2+tol]) sphere(d=1);
        
        translate([-1/2,headW/2-tol-1/2,slotTH+headTH-1/2-tol]) sphere(d=1);
        translate([-(slotW-tol)/2,headW/2-tol-(slotW-tol)/2,slotTH+headTH-1/2-tol]) rotate_extrude() translate([(slotW-tol)/2-1/2,0]) circle(d=1);
        translate([-(slotW-tol)/2,-headW/2+tol+(slotW-tol)/2,slotTH+headTH-1/2-tol]) rotate_extrude() translate([(slotW-tol)/2-1/2,0]) circle(d=1);
        translate([-(slotW-tol)+1/2,-headW/2+tol+1/2,slotTH+headTH-1/2-tol]) sphere(d=1);
        
        translate([-(slotW-tol)/2,0,slotTH+headTH+1]) rotate_extrude() translate([(slotW-tol)/2-1/2,0]) circle(d=1);
    }
}

    // ===== ===== ===== Pins ===== ===== =====
module pin(diam,leng) color([0.7,0.7,0.7]) hull()
{
    translate([0,0,leng/2-(diam*0.2)]) cylinder(d1=diam, d2=diam*0.8, h=diam*0.2);
    translate([0,0,-leng/2]) cylinder(d2=diam, d1=diam*0.8, h=diam*0.2);
}
