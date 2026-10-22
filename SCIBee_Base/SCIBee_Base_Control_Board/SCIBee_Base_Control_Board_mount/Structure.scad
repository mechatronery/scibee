//include <Hardware.scad>
/*
$fn=60;
tol=0.1;
layW=0.45;
layH=0.15;
*/

//BOX();
//Standoff();
//linear_extrude(5) Spring(curveD=6,springTH=0.45*4,length=20,startW=9,endW=20);
//for(i=[-1:1:1]) ChamferedPuck_cutout(diam=8,chamf=2,thick=3,part=i);
//honeycomb(hexW=5,TH=1,hexSP=0.45*2,rowN=2,columN=3);
//fan_grill();
//Spring(curveD=18,springTH=6-tol*2,length=30,startW=6-tol*2,endW=6-tol*2);
//hole_overhang_cutout(diamOUT=20, diamIN=10);




module roundedBOX(dimX=100,dimY=100,dimZ=100,cornR=2) hull() for(i=[-1:2:1]) for(j=[-1:2:1]) for(k=[-1:2:1]) translate([i*(dimX/2-cornR),j*(dimY/2-cornR),k*(dimZ/2-cornR)]) sphere(r=cornR);

module Standoff(diam=6, heigh=5, holeSIZE="M3", holeTYPE="Insert") difference()
{
    union()
    {
        cylinder(d1=diam+heigh, d2=diam, h=heigh/2);
        cylinder(d=diam, h=heigh);
    }
    
    // hole cutout
    if(holeTYPE == "threadHole" || holeTYPE == "Insert" || holeTYPE == "threadNut") translate([0,0,heigh+0.5]) rotate([180,0,0]) Bolt_cutout(size=holeSIZE, length=heigh+1, insert_extention=1, type="Flat", thread=heigh, layer=0);
        if(holeTYPE == "Insert") translate([0,0,heigh]) rotate([180,0,0]) ThreadedInsert(size=holeSIZE, length=heigh*0.6, insert_extention=0.1);
        if(holeTYPE == "Hole" || holeTYPE == "Insert") translate([0,0,heigh+0.5]) rotate([180,0,0]) Bolt_cutout(size=holeSIZE, length=heigh+1, insert_extention=1, type="Flat", thread=heigh, layer=0);
}

module ChamferedPuck(diam=8,chamfT=2,chamfB=2,thick=3)
{
    translate([0,0,thick/2-chamfT/2]) cylinder(d1=diam, d2=diam-chamfT, h=chamfT/2);
    translate([0,0,-thick/2]) cylinder(d2=diam, d1=diam-chamfB, h=chamfB/2);
}

module ChamferedPuck_cutout(diam=8,chamf=2,thick=3,part=0)
{
    if(abs(part)==1) rotate([-part*90+90,0,0]) translate([0,0,thick/2]) cylinder(d1=diam, d2=diam+chamf*2, h=chamf, center=true);
    else cylinder(d=diam, h=thick, center=true);
}

module Spring(curveD,springTH,length,startW,endW) translate([curveD/2-springTH,0])
{
        spacing=curveD-springTH;
        cone=(endW-startW)/length/2;
        num=ceil(length/spacing);
    for(i=[1:2:num]) difference()
    {
        union()
        {
            hull()
            {
                translate([spacing*(i-1),curveD/2-(startW/2+cone*i*spacing)]) circle(d=curveD);
                translate([spacing*(i-1),-1/2]) square([curveD,1], center=true);
            }
            hull()
            {
                translate([spacing*i,-curveD/2+(startW/2+cone*i*spacing)]) circle(d=curveD);
                translate([spacing*i,1/2]) square([curveD,1], center=true);
            }
        }
        
        hull()
        {
            translate([spacing*(i-1),curveD/2-(startW/2+cone*i*spacing)]) circle(d=curveD-springTH*2);
            translate([spacing*(i-1),curveD/2]) circle(d=curveD-springTH*2);
        }
        hull()
        {
            translate([spacing*i,-curveD/2+(startW/2+cone*i*spacing)]) circle(d=curveD-springTH*2);
            translate([spacing*i,-curveD/2]) circle(d=curveD-springTH*2);
        }
    }
        
}

module honeycomb(hexW=5,TH=1,hexSP=0.45*2,rowN=1,columN=1) for(j=[-(rowN-1)/2:2:(rowN-1)/2]) for(i=[-(columN-1)/2:1:(columN-1)/2]) translate([j*sin(60)*((hexW+tol*2)+hexSP),i*((hexW+tol*2)+hexSP),0])
{
    cylinder(d=2*(hexW+tol*2)/sqrt(3), h=TH, center=true, $fn=6);
    translate([sin(60)*((hexW+tol*2)+hexSP),cos(60)*((hexW+tol*2)+hexSP),0]) cylinder(d=2*(hexW+tol*2)/sqrt(3), h=TH, center=true, $fn=6);
}

module fan_grill(size=80)
{
        grillN=round((size/2*4/5)/(5+layW*2));
        grillW=((size/2*4/5)/grillN)-layW*2;
    // grill cutout
    for(i=[0:1:3]) for(j=[0:1:grillN-1]) rotate([0,0,-((PI*(size/5+j*(grillW+layW*2))/2-grillW-layW*2)*360/(2*PI*(size/5+j*(grillW+layW*2))))/2+i*90+j*90/2])
    {
        translate([size/5+j*(grillW+layW*2),0,0]) cylinder(d=grillW, h=8, center=true);
        rotate([0,0,(PI*(size/5+j*(grillW+layW*2))/2-grillW-layW*2)*360/(2*PI*(size/5+j*(grillW+layW*2)))]) translate([size/5+j*(grillW+layW*2),0,0]) cylinder(d=grillW, h=8, center=true);
        
        rotate_extrude(angle=(PI*(size/5+j*(grillW+layW*2))/2-grillW-layW*2)*360/(2*PI*(size/5+j*(grillW+layW*2)))) translate([size/5+j*(grillW+layW*2),0]) square([grillW,8], center=true);
    }
    
    // bolt cutout
    for(k=[0:1:3]) rotate([0,0,k*90])
    {
        if(size==80) translate([71.5/2,71.5/2,0]) cylinder(d=4, h=20, center=true);
    }
}

module hole_overhang_cutout(diamOUT=20, diamIN=10) intersection()
{
    cylinder(d=diamOUT, h=3*(layH*1.5));
    
    union()
    {
        translate([0,0,(layH*1.5)/2]) cube([diamIN,diamOUT,layH*1.51], center=true);
        
        translate([0,0,layH*1.5+(layH*1.5)/2]) intersection()
        {
            cube([diamIN,diamOUT,layH*1.51], center=true);
            rotate([0,0,120]) cube([diamIN,diamOUT,layH*1.51], center=true);
        }
        translate([0,0,layH*1.5+layH*1.5+(layH*1.5)/2]) intersection()
        {
            intersection()
            {
                cube([diamIN,diamOUT,layH*1.51], center=true);
                rotate([0,0,120]) cube([diamIN,diamOUT,layH*1.51], center=true);
            }
            rotate([0,0,120*2]) cube([diamIN,diamOUT,layH*1.51], center=true);
        }
    }
}