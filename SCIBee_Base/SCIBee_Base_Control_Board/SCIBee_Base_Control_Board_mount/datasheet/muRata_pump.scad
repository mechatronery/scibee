//$fn=120;
//MZB3004T04();

module MZB3005T06() // https://www.murata.com/-/media/webrenewal/products/mechatronics/fluid/microblower_mzb3005t06/mzb3005t06-datasheet.ashx?la=en-us&cvid=20250422010000000000
{
    color([0.1,0.1,0.1]) hull()
    {
        translate([9.5-1.25,9.5-1.25,2.3-1]) cylinder(r=1.25, h=1);
        translate([9.5-1.25,-9.5+1.25,2.3-1]) cylinder(r=1.25, h=1);
        translate([-9.5+1.25,9.5-1.25,2.3-1]) cylinder(r=1.25, h=1);
        translate([-9.5+1.25,-9.5+1.25,2.3-1]) cylinder(r=1.25, h=1);
    }
    color([184/255,115/255,51/255]) hull()
    {
        translate([9.5-1.25,9.5-1.25,0]) cylinder(r1=1.25-(2.3-1)/2, r2=1.25, h=2.3-1);
        translate([9.5-1.25,-9.5+1.25,0]) cylinder(r1=1.25-(2.3-1)/2, r2=1.25, h=2.3-1);
        translate([-9.5+1.25,9.5-1.25,0]) cylinder(r1=1.25-(2.3-1)/2, r2=1.25, h=2.3-1);
        translate([-9.5+1.25,-9.5+1.25,0]) cylinder(r1=1.25-(2.3-1)/2, r2=1.25, h=2.3-1);
    }
    
    color([0.7,0.7,0.7])
    {
        translate([4.5,-9.5-1.5,2.3-1.5]) hull()
        {
            translate([2/2-0.3,0.3,0]) cylinder(r=0.3, h=0.1, center=true);
            translate([-2/2+0.3,0.3,0]) cylinder(r=0.3, h=0.1, center=true);
            translate([0,2,0]) cube([2,1,0.1], center=true);
        }
        translate([-4.5,-9.5-1.5,2.3-1]) hull()
        {
            translate([2/2-0.3,0.3,0]) cylinder(r=0.3, h=0.1, center=true);
            translate([-2/2+0.3,0.3,0]) cylinder(r=0.3, h=0.1, center=true);
            translate([0,2,0]) cube([2,1,0.1], center=true);
        }
    }
}

module MZB1001T02() // https://www.murata.com/-/media/webrenewal/products/mechatronics/fluid/microblower_mzb1001t02/mzb1001t02-datasheet.ashx?la=en-us&cvid=20241203063211000000
{
    color([0.1,0.1,0.1]) difference()
    {
        union()
        {
            hull()
            {
                translate([20/2-0.5,20/2-0.5,0]) cylinder(r=0.5, h=1.85);
                translate([20/2-0.5,-20/2+0.5,0]) cylinder(r=0.5, h=1.85);
                translate([-20/2+0.5,20/2-0.5,0]) cylinder(r=0.5, h=1.85);
                translate([-20/2+1.5,-20/2+1.5,0]) cylinder(r=1.5, h=1.85);
            }
            cylinder(d=4, h=1.85+0.6);
            cylinder(d=2, h=1.85+1.6);
        }
        
        translate([16.5/2,16.5/2,-0.05/2]) cylinder(d=1.7, h=1.9);
        translate([-16.5/2,16.5/2,-0.05/2]) cylinder(d=1.7, h=1.9);
        translate([-16.5/2,-16.5/2,-0.05/2]) cylinder(d=1.7, h=1.9);
        intersection()
        {
            translate([16.5/2,-16.5/2,-0.05/2]) cylinder(d=3, h=1.9);
            translate([16.5/2,-16.5/2,1.85/2]) cube([3,1.7,1.9], center=true);
        }
    }
    
    color([0.7,0.7,0.7])
    {
        translate([6/2-2/2,-20/2-(22.5-20),0]) hull()
        {
            translate([2/2-0.3,0.3,0]) cylinder(r=0.3, h=0.1);
            translate([-2/2+0.3,0.3,0]) cylinder(r=0.3, h=0.1);
            translate([0,2,0.1/2]) cube([2,1,0.1], center=true);
        }
        translate([-6/2+2/2,-20/2-(22.5-20),0]) hull()
        {
            translate([2/2-0.3,0.3,0]) cylinder(r=0.3, h=0.1);
            translate([-2/2+0.3,0.3,0]) cylinder(r=0.3, h=0.1);
            translate([0,2,0.1/2]) cube([2,1,0.1], center=true);
        }
    }
}

module MZB3004T04() // https://www.murata.com/-/media/webrenewal/products/mechatronics/fluid/microblower_mzb3004t04/mzb3004t04-datasheet.ashx?la=en-us&cvid=20250422010000000000
{
    color([0.1,0.1,0.1])
    {
        hull()
        {
            translate([21/2,19/2,3.4-1/2]) rotate([0,0,45]) translate([-1.8/2-1.8/2,0,0]) cube([1.8,1.8,1], center=true);
            mirror([1,0,0]) translate([21/2,19/2,3.4-1/2]) rotate([0,0,45]) translate([-1.8/2-1.8/2,0,0]) cube([1.8,1.8,1], center=true);
            translate([21/2-1.5,-19/2+1.5,3.4-1]) cylinder(r=1.5, h=1);
            translate([-21/2+1.5,-19/2+1.5,3.4-1]) cylinder(r=1.5, h=1);
        }
        
        hull()
        {
            translate([21/2,19/2,3.4-2+1/2]) rotate([0,0,45]) translate([-1.8/2-1.8/2,0,0]) cube([1.4,1.4,1], center=true);
            mirror([1,0,0]) translate([21/2,19/2,3.4-2+1/2]) rotate([0,0,45]) translate([-1.8/2-1.8/2,0,0]) cube([1.4,1.4,1], center=true);
            translate([21/2-1.5,-19/2+1.5/2,3.4-2]) cylinder(r=1, h=1);
            translate([-21/2+1.5,-19/2+1.5/2,3.4-2]) cylinder(r=1, h=1);
        }
        
        translate([0,0,3]) cylinder(d=4.8, h=0.8+(3.4-3));
        translate([0,0,3]) cylinder(d=2.6, h=4.5+(3.4-3));
            translate([0,0,3+(4.5+(3.4-3))]) cylinder(d1=2.6, d2=2, h=1);
    }
    
    color([184/255,115/255,51/255]) hull()
    {
        translate([21/2-2,19/2-2,0]) cylinder(r1=1.25-(3.4-2)/2, r2=1.25, h=3.4-2);
        translate([21/2-2,-19/2+2,0]) cylinder(r1=1.25-(3.4-2)/2, r2=1.25, h=3.4-2);
        translate([-21/2+2,19/2-2,0]) cylinder(r1=1.25-(3.4-2)/2, r2=1.25, h=3.4-2);
        translate([-21/2+2,-19/2+2,0]) cylinder(r1=1.25-(3.4-2)/2, r2=1.25, h=3.4-2);
    }
    
    color([0.7,0.7,0.7])
    {
        translate([-4.5,-19.5/2-1.5,3.4-2]) hull()
        {
            translate([2/2-0.3,0.3,0]) cylinder(r=0.3, h=0.1, center=true);
            translate([-2/2+0.3,0.3,0]) cylinder(r=0.3, h=0.1, center=true);
            translate([0,2,0]) cube([2,1,0.1], center=true);
        }
        translate([1.5,-19.5/2-1.5,3.4-2]) hull()
        {
            translate([2/2-0.3,0.3,0]) cylinder(r=0.3, h=0.1, center=true);
            translate([-2/2+0.3,0.3,0]) cylinder(r=0.3, h=0.1, center=true);
            translate([0,2,0]) cube([2,1,0.1], center=true);
        }
    }
}