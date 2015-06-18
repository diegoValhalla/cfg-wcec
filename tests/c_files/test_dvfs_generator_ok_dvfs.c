
/*** auto generate DVFS code ***/
#include "cfg_wcec.h"
__cfg_edge_type __cfg_type;
float __cfg_rwcec_bi;
float __cfg_rwcec_bj;
int __cfg_loop_max_iter;

int main() {
    int a, b;

    a = 2;
    b = 3;
    if (a < b) {
        a += 2*b;
        a += 2*b;
        a *= 5;
    } else {

        /*** auto generate DVFS code ***/
        __cfg_type = __CFG_TYPE_B;
        __cfg_rwcec_bi = 551;
        __cfg_rwcec_bj = 540;
        __cfg_change_freq(&__cfg_type, __cfg_rwcec_bi, __cfg_rwcec_bj, 0, 0);

        if (a > b) {
            a++;
            a *= 5;
        } else {

            /*** auto generate DVFS code ***/
            __cfg_type = __CFG_TYPE_B;
            __cfg_rwcec_bi = 524;
            __cfg_rwcec_bj = 507;
            __cfg_change_freq(&__cfg_type, __cfg_rwcec_bi, __cfg_rwcec_bj, 0, 0);

            a--;
        }
    }

    /*** auto generate DVFS code ***/
    __cfg_type = __CFG_TYPE_L;
    __cfg_rwcec_bi = 96;
    __cfg_rwcec_bj = 16;
    __cfg_loop_max_iter = 5;
    int __cfg_loop19_iter = 0;


    while (a > b) { //@LOOP 5

        /*** auto generate DVFS code ***/
        __cfg_loop19_iter++;

        a--;
        if (a < b) {
            a += 2*b;
            a *= 5;
        } else {

            /*** auto generate DVFS code ***/
            __cfg_type = __CFG_TYPE_B;
            __cfg_rwcec_bi = 428;
            __cfg_rwcec_bj = 408;
            __cfg_change_freq(&__cfg_type, __cfg_rwcec_bi, __cfg_rwcec_bj, 0, 0);

            a += 2*b;
        }
    }


    /*** auto generate DVFS code ***/
    __cfg_change_freq(&__cfg_type, __cfg_rwcec_bi, __cfg_rwcec_bj, __cfg_loop_max_iter, __cfg_loop19_iter);

    return 0;
}
